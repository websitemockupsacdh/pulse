// The API may return naive UTC timestamps. Treat them as UTC.
export const utc = (s: string) => new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(s) ? s : s + "Z");

export function ago(s: string): string {
  const m = Math.max(0, Math.round((Date.now() - utc(s).getTime()) / 60000));
  if (m < 1) return "just now";
  if (m < 60) return `${m} min ago`;
  if (m < 1440) return `${Math.round(m / 60)} h ago`;
  return `${Math.round(m / 1440)} d ago`;
}
export const stamp = (s: string) =>
  utc(s).toLocaleString("en-PH", { timeZone: "Asia/Manila", dateStyle: "medium", timeStyle: "short" }) + " PHT";
export const num = (n: number) => new Intl.NumberFormat("en-PH", { notation: "compact" }).format(n);
