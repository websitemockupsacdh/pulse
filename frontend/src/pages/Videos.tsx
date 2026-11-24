import { ErrorBox, ItemList, Loading, PageHead, Section } from "../components/ui";
import { useApi } from "../lib/api";
import type { Item } from "../lib/types";

export default function Videos() {
  const { data, error, loading } = useApi<Item[]>("/feed", { kind: "video", limit: "100" });
  const g = (s: Item["live_status"]) => (data ?? []).filter((i) => i.live_status === s);
  const rest = (data ?? []).filter((i) => !i.live_status);
  return (
    <>
      <PageHead title="Videos & Live" lede="Via the official YouTube Data API. A stream counts as live only when YouTube reports it as live, never because of its title. Videos open on YouTube." />
      {error && <ErrorBox msg={error} />}
      {loading ? <Loading /> : (
        <>
          <Section title="Live now"><ItemList items={g("live")} showEngagement empty="No stream is reported live by YouTube right now." /></Section>
          <Section title="Upcoming streams"><ItemList items={g("upcoming")} showEngagement empty="No upcoming streams reported." /></Section>
          <Section title="Recently completed streams"><ItemList items={g("completed")} showEngagement empty="None reported." /></Section>
          <Section title="Trending videos"><ItemList items={rest} showEngagement empty="No trending videos collected. The YouTube connector needs an API key on the backend." /></Section>
        </>
      )}
    </>
  );
}
