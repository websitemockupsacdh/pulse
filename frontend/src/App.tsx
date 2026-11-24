import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Category, { CATEGORY_PAGES } from "./pages/Category";
import Home from "./pages/Home";
import Search from "./pages/Search";
import TopicPage from "./pages/Topic";
import Trending from "./pages/Trending";
import Weather from "./pages/Weather";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="trending" element={<Trending />} />
        <Route path="weather" element={<Weather />} />
        <Route path="search" element={<Search />} />
        <Route path="topic/:slug" element={<TopicPage />} />
        {Object.keys(CATEGORY_PAGES).map((p) => <Route key={p} path={p} element={<Category page={p} />} />)}
        <Route path="*" element={<p className="py-20 font-serif text-3xl">Page not found.</p>} />
      </Route>
    </Routes>
  );
}
