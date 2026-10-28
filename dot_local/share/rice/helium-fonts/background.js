// Read the generated settings on install, browser startup and every 30 seconds.
// Only generic font preferences change. Font sizes and website CSS are preserved.
async function applyFonts() {
  const response = await fetch(chrome.runtime.getURL("fonts.json"), {cache: "no-store"});
  if (!response.ok) throw new Error("Rice fonts.json unavailable");
  const fonts = await response.json();
  for (const [genericFamily, fontId] of [["standard", fonts.interface], ["sansserif", fonts.interface], ["fixed", fonts.monospace]]) {
    if (typeof fontId !== "string" || !fontId) throw new Error("Invalid Rice font family");
    const current = await chrome.fontSettings.getFont({genericFamily});
    if (current.fontId !== fontId) await chrome.fontSettings.setFont({genericFamily, fontId});
  }
}
function refresh() { applyFonts().catch(error => console.warn("Rice Fonts:", error.message)); }
chrome.runtime.onInstalled.addListener(refresh);
chrome.runtime.onStartup.addListener(refresh);
chrome.alarms.onAlarm.addListener(refresh);
chrome.alarms.create("rice-fonts", {periodInMinutes: 0.5});
refresh();
