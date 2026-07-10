/**
 * Record index for the MCP server.
 *
 * `id` matches the page filename stem under /reports/. Every summary here is
 * drawn from the signed report reproduced on the corresponding page — nothing
 * is inferred. `get_record` can fetch the full page text on demand.
 */

export const PATIENT = {
  name: "Tyler Bishop",
  sex: "male",
  dob: "1987-05-26",
  site: "https://helptyler.live",
  published_by: "the patient, deliberately and publicly",
};

export const RECORDS = [
  {
    id: "2026-07-06-mri-right-shoulder",
    date: "2026-07-06",
    title: "MRI Right Shoulder, Without Contrast",
    category: "imaging",
    status: "abnormal",
    summary:
      "Large glenohumeral joint effusion with distention of the subscapularis recess. Large effusion throughout the subcoracoid bursa with fluid tracking superficial to the subscapularis muscle. Small amount of fluid at the subacromial bursa. Ill-defined interstitial tearing of the supraspinatus tendon up to 2.3 x 2.3 cm; no well-defined full-thickness defect. Moderate subscapularis tendinosis with suspected ill-defined tear near the inferior musculotendinous junction. Interval rotator cuff repair; evidence of acromioplasty; suture anchors at the greater tuberosity. Mild glenohumeral DJD. Long biceps tendon intact. Radiologist: Benjamin Eyer. Comparison: MRI 2025-07-23.",
  },
  {
    id: "2026-07-02-protein-electrophoresis",
    date: "2026-07-02",
    title: "Serum Protein Electrophoresis and Free Light Chains",
    category: "immunology",
    status: "normal",
    summary:
      "SPEP normal pattern with NO monoclonal protein: 'No specific abnormalities seen and no abnormalities suggestive of the presence of monoclonal protein.' Total protein 6.5 g/dL (6.1-8.1). Albumin 4.5, alpha-1 0.2, alpha-2 0.5, beta-1 0.4, beta-2 0.3, gamma globulin 0.7. Serum free kappa light chain 10.6 mg/L (3.3-19.4), collected 2026-06-29. IMPORTANT LIMIT: free lambda and the kappa/lambda ratio were NOT ordered, and serum immunofixation was not performed, so a low-level clonal light-chain process (AL amyloidosis, light-chain MGUS) is not fully excluded.",
  },
  {
    id: "2026-07-02-ana-screen",
    date: "2026-07-02",
    title: "ANA Screen with Reflex",
    category: "immunology",
    status: "negative",
    summary:
      "ANA Screen by indirect immunofluorescence (IFA): NEGATIVE. No reflex titer or pattern performed. This is the second negative ANA on record (prior negative 2024-11-18).",
  },
  {
    id: "2026-02-24-coagulation-vwf",
    date: "2026-02-24",
    title: "Coagulation and von Willebrand Panel",
    category: "coagulation",
    status: "abnormal",
    summary:
      "Factor VIII activity 147% (ref 56-140) HIGH on the vWF panel; 137% on the coagulation panel (ref 57-163). vWF antigen 143% and vWF activity 126% — both normal, excluding von Willebrand disease. Factor IX 91%, Factor XI 90%, fibrinogen 226 mg/dL, APTT 28.2 s, PT 10.8 s, INR 1.0, D-dimer 0.37. All six antiphospholipid antibodies negative — second confirmation after 2026-01-16. Elevated Factor VIII is an acute-phase reactant and an independent VTE risk factor; it does not explain the hemarthrosis.",
  },
  {
    id: "2026-02-24-uric-acid",
    date: "2026-02-24",
    title: "Uric Acid",
    category: "chemistry",
    status: "normal",
    summary:
      "Serum uric acid 5.6 mg/dL (ref 3.8-8.4). Normal — excludes gout and crystal arthropathy as the cause of recurrent joint inflammation.",
  },
  {
    id: "2026-02-17-abdominal-ultrasound",
    date: "2026-02-17",
    title: "Abdominal Ultrasound, Complete",
    category: "imaging",
    status: "abnormal",
    summary:
      "Diffusely increased hepatic parenchymal echogenicity, nonspecific but typical of fatty infiltration and/or hepatocellular disease. Liver length 16.0 cm. Contracted gallbladder with a tiny 3 mm intraluminal polyp. CBD 3 mm. Right kidney 11.8 cm, left 12.6 cm, spleen 11.4 cm — all normal. Indication: abnormal liver function tests, esophagitis. Radiologist: Juan Carlos Vera. Comparison: 2018-07-30, when liver echogenicity was normal.",
  },
  {
    id: "2026-01-19-ldh-isoenzymes",
    date: "2026-01-19",
    title: "LDH Isoenzymes (LD Fractions)",
    category: "chemistry",
    status: "borderline",
    summary:
      "Total LDH 231 IU/L (ref 121-224), mildly elevated, as on 2026-01-16 (232). All five LD fractions normal: LD1 31%, LD2 34%, LD3 20%, LD4 8%, LD5 7%. Normal LD1/LD2 ratio excludes acute myocardial infarction and hemolysis; normal LD4/LD5 argues against active liver or muscle damage.",
  },
  {
    id: "2026-01-16-cbc-cmp",
    date: "2026-01-16",
    title: "CBC, CMP, ESR, CRP",
    category: "chemistry",
    status: "normal",
    summary:
      "KEY FINDING: ESR 2 mm/hr and CRP <1 mg/L — systemic inflammatory markers are suppressed despite active multi-system disease. WBC 5.6, hemoglobin 13.7 g/dL, hematocrit 41.6%, platelets 324, MCV 89. Neutrophils 52% (2.9 abs), lymphocytes 34%. Glucose 78, BUN 13, creatinine 0.95, eGFR 105, calcium 10.2, AST 26, ALT 25, albumin 4.9, total bilirubin 1.1.",
  },
  {
    id: "2026-01-16-coagulation",
    date: "2026-01-16",
    title: "Coagulation Panel (Factor V Leiden, Antiphospholipid)",
    category: "coagulation",
    status: "negative",
    summary:
      "Factor V Leiden negative. Antiphospholipid antibody panel (all six antibodies) negative. Initial coagulation workup after the 2026-01-04 hemarthrosis.",
  },
  {
    id: "2026-01-16-creatinine-urine",
    date: "2026-01-16",
    title: "24-Hour Urine Creatinine",
    category: "chemistry",
    status: "normal",
    summary: "24-hour urine creatinine 1861 mg/24 hr (ref 1000-2000). Normal renal creatinine clearance confirmed.",
  },
  {
    id: "2026-01-16-tryptase-c1",
    date: "2026-01-16",
    title: "Tryptase, C1 Esterase Inhibitor",
    category: "immunology",
    status: "normal",
    summary:
      "Tryptase 5.9 µg/L (ref 2.2-13.2), stable from 6.0 on 2026-01-12. C1 esterase inhibitor normal. Note: a normal serum tryptase does NOT exclude hereditary alpha-tryptasemia, which requires TPSAB1 copy-number testing.",
  },
  {
    id: "2026-01-16-urinalysis",
    date: "2026-01-16",
    title: "Urinalysis, LDH, GGT",
    category: "chemistry",
    status: "borderline",
    summary:
      "Urine pH 8.0 (alkaline) and specific gravity <1.005 (dilute). LDH 232 IU/L, mildly elevated. GGT 15 IU/L normal. All other urinalysis markers negative.",
  },
  {
    id: "2026-01-12-c1-tryptase",
    date: "2026-01-12",
    title: "C1 Esterase, Tryptase, Complement",
    category: "immunology",
    status: "normal",
    summary:
      "Tryptase 6.0 µg/L (ref 2.2-13.2). C1 esterase inhibitor, serum 29 mg/dL (ref 21-39). Complement C1q 12.6 mg/dL (ref 10.2-20.3). Initial angioedema and mast-cell workup after the hemarthrosis. All within normal limits.",
  },
  {
    id: "2026-01-04-synovial",
    date: "2026-01-04",
    title: "Synovial Fluid Analysis, Right Elbow",
    category: "synovial",
    status: "critical",
    summary:
      "SPONTANEOUS HEMARTHROSIS. 22.0 mL aspirated from the right elbow. Color red, appearance bloody. RBC 3,197,000/µL (ref <15,000). Nucleated cell count 2,570/µL (ref 0-200). Neutrophils 68% (ref <25), lymphocytes 23%, mononuclears 8%, basophils 1%. No crystals reported. Ordering provider Wynne Myint, MD; Torrey Pines Lab. Subsequent workup found no inherited coagulopathy, no vWD, no antiphospholipid syndrome, and no crystal arthropathy — the cause remains undetermined.",
  },
  {
    id: "2025-07-17-cbc-cmp",
    date: "2025-07-17",
    title: "CBC, CMP, Lipids",
    category: "chemistry",
    status: "normal",
    summary:
      "Complete blood count and metabolic panel normal. Liver enzymes normalized (AST 31, ALT 30) from the 2024-11-18 elevation. Hemoglobin 14.1 g/dL, hematocrit 42.7%.",
  },
  {
    id: "2025-05-08-mra-neck",
    date: "2025-05-08",
    title: "MRA Neck, With and Without Contrast",
    category: "imaging",
    status: "negative",
    summary:
      "Indication: pressure in neck with exertion, evaluate for vertebrobasilar insufficiency. No hemodynamically significant stenosis or dissection in any vessel — common, internal and external carotid and vertebral arteries, bilaterally. Bones, base of neck and lung apices unremarkable. IMPORTANT LIMIT: the radiologist flagged the study as 'suboptimal examination secondary to venous contamination,' which reduces sensitivity. Contrast: Gadavist 10 mL. Ordered by Zachary Fellows, MD; read by Eric Chou, MD.",
  },
  {
    id: "2024-11-18-rheumatology",
    date: "2024-11-18",
    title: "Rheumatology / Autoimmune Panel",
    category: "immunology",
    status: "abnormal",
    summary:
      "Every classical adaptive-autoimmunity marker is negative: ANA negative, rheumatoid factor <10 IU/mL, anti-CCP <20 U, anti-SS-A <0.2, anti-SS-B <0.2, anti-Smith <0.2, anti-dsDNA <1 IU/mL, anti-U1-RNP <20 U, anti-DFS70 <20 U, HLA-B27 negative, tTG IgA <2 U/mL (celiac negative). C3 93, C4 15 (low-normal). Infectious screening negative: HBsAg negative, HCV non-reactive, hepatitis B core Ab negative, QuantiFERON-TB negative; hepatitis B surface Ab 34,415 mIU/mL (immune). AST 62 and ALT 95 both HIGH at this draw (since normalized).",
  },
  {
    id: "2024-05-13-dermatopathology",
    date: "2024-05-13",
    title: "Dermatopathology, Right Jawline Shave Biopsy",
    category: "pathology",
    status: "abnormal",
    summary:
      "Case D24-10572. Diagnosis: superficial epidermal necrosis with paucicellular dermal mixed inflammation and hemorrhage. Direct immunofluorescence: NEGATIVE for IgG, IgA, IgM and C3 — excludes autoimmune blistering disease. Microscopy: abrupt superficial epidermal necrosis; basal layer viable; no acantholytic keratinocytes; no vesicle. Dermal perivascular and interstitial infiltrate of lymphocytes, histiocytes and NEUTROPHILS. NO EOSINOPHILS. Extravasated red blood cells present but NO leukocytoclastic vasculitis. No suppurative folliculitis, granulomatous inflammation, or interface dermatitis. Fungal (PASF) and tissue Gram stains negative. Pathologist's comment: 'The histopathologic features are not specific. The possibility of an irritant contact dermatitis is considered.' Tissue exhausted from the block — no further stains possible on this specimen. Collected 2024-04-26; pathologist Cora Sue Humberson, MD.",
  },
  {
    id: "2023-04-27-allergies",
    date: "2023-04-27",
    title: "Focused Allergen Panel",
    category: "allergy",
    status: "negative",
    summary: "Follow-up allergen-specific IgE testing. All allergens negative. Low total IgE.",
  },
  {
    id: "2020-02-07-renal",
    date: "2020-02-07",
    title: "Renal Panel, Electrolytes, Urinalysis",
    category: "chemistry",
    status: "normal",
    summary: "Kidney function assessment normal. Bilirubin normalized from the 2018 elevation.",
  },
  {
    id: "2018-08-28-allergies",
    date: "2018-08-28",
    title: "Allergy Panel, CBC, CMP",
    category: "allergy",
    status: "borderline",
    summary:
      "Comprehensive allergen-specific IgE testing: all negative. Total bilirubin 1.5 mg/dL (elevated, later normalized — likely Gilbert's syndrome). Vitamin B12 1728 pg/mL (elevated, ref 232-1245; consistent with supplementation).",
  },
  {
    id: "2018-07-30-abdominal-ultrasound",
    date: "2018-07-30",
    title: "Abdominal Ultrasound, Complete",
    category: "imaging",
    status: "normal",
    summary:
      "BASELINE. Liver length 16.8 cm with NORMAL parenchymal echogenicity — contrast with the 2026-02-17 study showing diffusely increased echogenicity. 3 mm gallbladder polyp (unchanged at 3 mm in 2026). CBD 2.3 mm. Right kidney 9.9 cm, left kidney 12.4 cm, spleen 12.0 cm, pancreas normal. No aneurysm. Indication: generalized abdominal pain and anemia. Conclusion: small gallbladder polyp, otherwise negative. Radiologist: Rowena G. Tena, MD.",
  },
  {
    id: "2017-12-18-baseline",
    date: "2017-12-18",
    title: "Baseline Labs (CBC, CMP, Lipids)",
    category: "chemistry",
    status: "normal",
    summary: "Initial baseline. All values normal. Hemoglobin 13.8 g/dL, glucose 90, creatinine 1.00.",
  },
  {
    id: "2017-07-05-breast-ultrasound",
    date: "2017-07-05",
    title: "Right Breast Ultrasound, Complete",
    category: "imaging",
    status: "abnormal",
    summary:
      "Right retroareolar palpable lump. Immediately subdermal hypoechoic mass 2.3 x 1.6 x 0.6 cm, heterogeneous, without apparent vascularity, appearing associated with the skin and/or nipple; 'No appreciable breast tissue.' Assessment BI-RADS Category 2 (benign). Radiologist's comment: the mass 'appears most likely related to the dermis rather than gynecomastia.' Patient reported first noticing the lump ~5 years earlier (c. 2012); it resolved and recurred. The mass was excised in August 2017; that surgical pathology is NOT present in this record set. Radiologist: Michael L. Tobin, MD.",
  },
  {
    id: "2017-07-05-thyroid-ultrasound",
    date: "2017-07-05",
    title: "Thyroid Ultrasound",
    category: "imaging",
    status: "normal",
    summary:
      "Indication: thyroid nodule. Right lobe 4.7 x 1.7 x 1.9 cm, left lobe 3.4 x 1.0 x 1.1 cm, isthmus 0.3 cm. All homogeneous with no visible mass, cyst, or calcification. Conclusion: normal examination — the suspected nodule was not confirmed. Radiologist: Michael L. Tobin, MD.",
  },
];

for (const r of RECORDS) {
  r.path = `/reports/${r.id}`;
  r.url = `${PATIENT.site}${r.path}`;
}

export const CATEGORIES = [...new Set(RECORDS.map((r) => r.category))].sort();
