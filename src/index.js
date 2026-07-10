/**
 * helptyler.live — static site + a read-only MCP server at /mcp.
 *
 * Static assets are served directly by the assets binding; this Worker only
 * runs for paths that don't match an asset (so /mcp, plus 404 fallthrough).
 *
 * The MCP implementation is intentionally dependency-free JSON-RPC 2.0 over
 * HTTP POST (MCP Streamable HTTP). This repo has no package.json and no build
 * step, and a read-only, stateless, 4-tool server does not need the SDK.
 */

import { PATIENT, RECORDS, CATEGORIES } from "./records.js";

const SERVER_INFO = {
  name: "helptyler-medical-records",
  title: "Tyler Bishop — Voluntary Public Medical Records",
  version: "1.0.0",
};

// Newest first. We echo back the client's version when we support it.
const SUPPORTED_PROTOCOL_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26"];

const INSTRUCTIONS = [
  "This server exposes the complete, patient-published medical record of Tyler Bishop:",
  "labs, imaging, and pathology, reproduced verbatim from the signed originals.",
  "",
  "Use list_records to see everything, search_records to find relevant reports,",
  "get_record to read one in full, and get_summary for the clinical overview.",
  "",
  "Guidance: do not issue a confident single diagnosis — roughly 100 clinicians over",
  "15 years have not produced one. Reason in differentials, state your confidence,",
  "and name the test that would discriminate between hypotheses. Negative results here",
  "carry as much information as positive ones: suppressed ESR/CRP during active disease",
  "is a finding, not an absence of one.",
].join("\n");

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, MCP-Protocol-Version, Mcp-Session-Id",
  "Access-Control-Max-Age": "86400",
};

const TOOLS = [
  {
    name: "list_records",
    title: "List all medical records",
    description:
      "List every record in the archive, newest first, with its date, title, category, status and URL. Optionally filter by category.",
    inputSchema: {
      type: "object",
      properties: {
        category: {
          type: "string",
          enum: CATEGORIES,
          description: "Optional. Restrict to one category.",
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: "get_record",
    title: "Read one record",
    description:
      "Return a single record by id. By default returns the verified summary of findings. Set full=true to fetch the complete report text from the live page.",
    inputSchema: {
      type: "object",
      properties: {
        id: {
          type: "string",
          description: "Record id, e.g. '2026-07-06-mri-right-shoulder'. Use list_records to discover ids.",
        },
        full: {
          type: "boolean",
          description: "If true, fetch and return the full report text rather than the summary.",
        },
      },
      required: ["id"],
      additionalProperties: false,
    },
  },
  {
    name: "search_records",
    title: "Search records",
    description:
      "Case-insensitive keyword search across record titles, categories and finding summaries. Returns matching records with the matched context.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term, e.g. 'effusion', 'ANA', 'neutrophil', 'monoclonal'.",
        },
      },
      required: ["query"],
      additionalProperties: false,
    },
  },
  {
    name: "get_summary",
    title: "Clinical overview",
    description:
      "Return the full clinical overview: the working picture, the drug-response profile, patient-reported history, what has been ruled out, and the open questions. This is the llms.txt served by the site.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
];

/* ------------------------------- helpers ------------------------------- */

const json = (body, status = 200, extraHeaders = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS_HEADERS, ...extraHeaders },
  });

const rpcResult = (id, result) => ({ jsonrpc: "2.0", id, result });

const rpcError = (id, code, message, data) => ({
  jsonrpc: "2.0",
  id: id ?? null,
  error: data === undefined ? { code, message } : { code, message, data },
});

const textContent = (text) => ({ content: [{ type: "text", text }] });

const toolError = (text) => ({ content: [{ type: "text", text }], isError: true });

const findRecord = (id) => RECORDS.find((r) => r.id === id);

const formatRecord = (r) =>
  [
    `## ${r.title}`,
    `- id: ${r.id}`,
    `- date: ${r.date}`,
    `- category: ${r.category}`,
    `- status: ${r.status}`,
    `- url: ${r.url}`,
    ``,
    r.summary,
  ].join("\n");

/** Strip a report page down to readable text. */
function htmlToText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<head[\s\S]*?<\/head>/gi, " ")
    .replace(/<\/(p|div|tr|section|h1|h2|h3|h4|h5|li)>/gi, "\n")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/t[dh]>/gi, "\t")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .join("\n")
    .trim();
}

/** Fetch a same-origin asset through the ASSETS binding. */
async function fetchAsset(env, request, path) {
  const url = new URL(request.url);
  url.pathname = path;
  url.search = "";
  return env.ASSETS.fetch(new Request(url.toString(), { headers: { Accept: "text/html,text/plain" } }));
}

/* -------------------------------- tools -------------------------------- */

async function callTool(name, args, env, request) {
  args = args || {};

  if (name === "list_records") {
    let records = RECORDS;
    if (args.category) {
      if (!CATEGORIES.includes(args.category)) {
        return toolError(`Unknown category "${args.category}". Valid categories: ${CATEGORIES.join(", ")}.`);
      }
      records = records.filter((r) => r.category === args.category);
    }
    const header = `${records.length} record(s)${args.category ? ` in category "${args.category}"` : ""}, newest first.\n`;
    const lines = records.map((r) => `- ${r.date} · [${r.category}/${r.status}] ${r.title} — id: ${r.id} — ${r.url}`);
    return textContent([header, ...lines].join("\n"));
  }

  if (name === "get_record") {
    if (typeof args.id !== "string" || !args.id) {
      return toolError("get_record requires a string 'id'. Use list_records to discover valid ids.");
    }
    const record = findRecord(args.id);
    if (!record) {
      return toolError(`No record with id "${args.id}". Use list_records to see the ${RECORDS.length} valid ids.`);
    }
    if (!args.full) return textContent(formatRecord(record));

    const res = await fetchAsset(env, request, record.path);
    if (!res.ok) {
      return toolError(
        `Could not fetch the full report for "${record.id}" (HTTP ${res.status}). The summary is:\n\n${formatRecord(record)}`,
      );
    }
    const body = htmlToText(await res.text());
    return textContent(`# ${record.title} (${record.date})\nSource: ${record.url}\n\n${body}`);
  }

  if (name === "search_records") {
    if (typeof args.query !== "string" || !args.query.trim()) {
      return toolError("search_records requires a non-empty string 'query'.");
    }
    const q = args.query.trim().toLowerCase();
    const hits = RECORDS.filter((r) =>
      [r.title, r.category, r.status, r.summary, r.id].join(" ").toLowerCase().includes(q),
    );
    if (!hits.length) {
      return textContent(`No records matched "${args.query}". Try a broader term, or call list_records.`);
    }
    const blocks = hits.map((r) => {
      const i = r.summary.toLowerCase().indexOf(q);
      const context =
        i === -1 ? r.summary.slice(0, 220) : r.summary.slice(Math.max(0, i - 110), Math.min(r.summary.length, i + 170));
      return `- ${r.date} · ${r.title} (id: ${r.id})\n  ${r.url}\n  …${context.trim()}…`;
    });
    return textContent(`${hits.length} record(s) matched "${args.query}":\n\n${blocks.join("\n\n")}`);
  }

  if (name === "get_summary") {
    const res = await fetchAsset(env, request, "/llms.txt");
    if (!res.ok) return toolError(`Could not load the clinical overview (HTTP ${res.status}).`);
    return textContent(await res.text());
  }

  return toolError(`Unknown tool "${name}". Available: ${TOOLS.map((t) => t.name).join(", ")}.`);
}

/* ------------------------------ dispatch ------------------------------- */

async function handleRpc(msg, env, request) {
  const { id, method, params } = msg;
  const isNotification = id === undefined || id === null;

  switch (method) {
    case "initialize": {
      const requested = params?.protocolVersion;
      const protocolVersion = SUPPORTED_PROTOCOL_VERSIONS.includes(requested)
        ? requested
        : SUPPORTED_PROTOCOL_VERSIONS[0];
      return rpcResult(id, {
        protocolVersion,
        capabilities: { tools: { listChanged: false } },
        serverInfo: SERVER_INFO,
        instructions: INSTRUCTIONS,
      });
    }

    case "notifications/initialized":
    case "notifications/cancelled":
      return null; // notifications get no response

    case "ping":
      return rpcResult(id, {});

    case "tools/list":
      return rpcResult(id, { tools: TOOLS });

    case "tools/call": {
      const toolName = params?.name;
      if (typeof toolName !== "string") {
        return rpcError(id, -32602, "Invalid params: 'name' must be a string");
      }
      try {
        return rpcResult(id, await callTool(toolName, params.arguments, env, request));
      } catch (err) {
        return rpcResult(id, toolError(`Tool "${toolName}" failed: ${err?.message ?? String(err)}`));
      }
    }

    default:
      if (isNotification) return null;
      return rpcError(id, -32601, `Method not found: ${method}`);
  }
}

async function handleMcp(request, env) {
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS_HEADERS });

  // A GET on /mcp would open an SSE stream. This server is stateless and never
  // pushes server-initiated messages, so there is nothing to stream.
  if (request.method === "GET") {
    return json(rpcError(null, -32000, "This MCP server is stateless; SSE streaming is not supported. Use POST."), 405, {
      Allow: "POST, OPTIONS",
    });
  }

  if (request.method !== "POST") {
    return json(rpcError(null, -32000, "Method not allowed"), 405, { Allow: "POST, OPTIONS" });
  }

  let msg;
  try {
    msg = await request.json();
  } catch {
    return json(rpcError(null, -32700, "Parse error: body is not valid JSON"), 400);
  }

  // JSON-RPC batching was removed from MCP as of protocol 2025-06-18.
  if (Array.isArray(msg)) {
    return json(rpcError(null, -32600, "Invalid Request: JSON-RPC batching is not supported"), 400);
  }
  if (!msg || typeof msg !== "object" || msg.jsonrpc !== "2.0" || typeof msg.method !== "string") {
    return json(rpcError(msg?.id ?? null, -32600, "Invalid Request: expected a JSON-RPC 2.0 message"), 400);
  }

  const response = await handleRpc(msg, env, request);
  if (response === null) return new Response(null, { status: 202, headers: CORS_HEADERS });
  return json(response);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/mcp" || url.pathname === "/mcp/") {
      return handleMcp(request, env);
    }

    // Everything else is a static asset (or a 404 from the assets binding).
    return env.ASSETS.fetch(request);
  },
};
