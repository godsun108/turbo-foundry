// SoulX-Singer English phone inventory, mirrored from music-foundry/soulx_export.py.
// Keep this allowlist aligned with the upstream model's documented English phoneset.
export const SOULX_ENGLISH_PHONES = new Set([
  "AA0","AA1","AA2","AE0","AE1","AE2","AH0","AH1","AH2","AO0","AO1","AO2",
  "AW0","AW1","AW2","AY0","AY1","AY2","B","CH","D","DH","EH0","EH1","EH2",
  "ER0","ER1","ER2","EY0","EY1","EY2","F","G","HH","IH0","IH1","IH2","IY0",
  "IY1","IY2","JH","K","L","M","N","NG","OW0","OW1","OW2","OY0","OY1","OY2",
  "P","R","S","SH","T","TH","UH0","UH1","UH2","UW","UW0","UW1","UW2","V","W",
  "Y","Z","ZH"
]);

export function validateSoulXPhones(tokens) {
  if (!Array.isArray(tokens) || tokens.length === 0) return ["At least one ARPABET phone is required."];
  return tokens.flatMap((token, index) =>
    typeof token !== "string" || !SOULX_ENGLISH_PHONES.has(token)
      ? [`Phone ${index + 1} “${String(token)}” is not in the supported SoulX English phoneset.`]
      : []
  );
}
