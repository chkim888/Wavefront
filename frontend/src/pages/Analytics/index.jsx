import { getAllExperiments, getResult } from "@/api/experiments";
import { getAllProjects } from "@/api/projects";
import { getAllTopics, getPostsForTopic } from "@/api/topics";
import { useEffect, useMemo, useState } from "react";
import {
  PieChart,
  Pie,
  XAxis,
  YAxis,
  LineChart,
  Line,
  BarChart,
  Bar,
  Cell,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
  Tooltip,
} from "recharts";

function Analytics() {
  // set state variables
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [posts, setPosts] = useState([]);
  const [results, setResults] = useState([]);
  // color definition for charts
  const SENTIMENT_COLORS = {
    positive: "#77DD76", // Green
    neutral: "#FDFD96", // Yellow
    negative: "#FF6961", // Red
  };

  // page loads
  // load on initial page load
  useEffect(() => {
    const fetch = async () => {
      try {
        // set list of projects
        const res = await getAllProjects();
        setProjects(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, []);

  // load on project selection
  useEffect(() => {
    const fetch = async () => {
      if (!selectedProject) return;
      try {
        // get all topics
        const tp = await getAllTopics(selectedProject.id);
        setTopics(tp);
        // get all experiments
        const exp = await getAllExperiments(selectedProject.id);
        setExperiments(exp);
        // get results & set them
        const res = [];
        for (let i = 0; i < exp.length; i += 1) {
          const experimentId = exp[i].id;
          const response = await getResult(experimentId);
          res.push(response);
        }
        setResults(res);
        // reset
        setPosts([]);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedProject]);

  // load on topic selection
  useEffect(() => {
    const fetch = async () => {
      if (!selectedTopic) return;
      try {
        const res = await getPostsForTopic(selectedTopic.id);
        setPosts(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedTopic]);

  // other functions

  // calculating sentiment counts for selected topic
  const sentimentCounts = useMemo(() => {
    if (!posts?.length) return [];
    const aggregated = posts.reduce((counts, post) => {
      const sentiment = post.sentiment_label;
      counts[sentiment] = (counts[sentiment] || 0) + 1;
      return counts;
    }, {});
    return Object.entries(aggregated).map(([sentiment, count]) => ({
      sentiment,
      count,
    }));
  }, [posts]);

  // organizing sentiment data across time for a topic
  const sentimentTimeline = useMemo(() => {
    if (!posts?.length) return [];
    const postsByDate = posts.reduce((acc, post) => {
      // By month
      const date = post.posted_time.split("T")[0].slice(0, 7);
      if (!acc[date]) {
        acc[date] = { date, positive: 0, neutral: 0, negative: 0 };
      }
      acc[date][post.sentiment_label] += 1;
      return acc;
    }, {});
    return Object.values(postsByDate).sort(
      (a, b) => new Date(a.date) - new Date(b.date),
    );
  }, [posts]);

  // control vs. treatment conversion rates across experiments for a project
  const conversionRates = useMemo(() => {
    if (!results?.length) return [];
    const rates = results.reduce((acc, result) => {
      const title = experiments.find(
        (e) => e.id === result.experiment_id,
      )?.title;
      acc[title] = {
        title,
        control: result.control_conversions,
        treatment: result.treatment_conversions,
      };
      return acc;
    }, {});
    return Object.values(rates);
  }, [results, experiments]);

  // for styling
  const selectClass =
    "bg-[#1e2130] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 focus:outline-none focus:border-[#6366f1]";
  const cardClass = "bg-[#1e2130] border border-[#2a2d3e] rounded-xl p-6 mb-6";

  const tooltipStyle = {
    backgroundColor: "#1e2130",
    border: "1px solid #2a2d3e",
    borderRadius: "8px",
    color: "#f1f5f9",
  };

  // JSX
  return (
    <>
      <h1 className="text-white text-2xl font-bold mb-6">Analytics</h1>
      <div className="flex gap-4 mb-6">
        {/* Project selector */}
        <select
          className={selectClass}
          id="project-select"
          value={selectedProject?.name ?? ""}
          onChange={(e) =>
            setSelectedProject(projects.find((p) => p.name === e.target.value))
          }
        >
          <option value="" disabled hidden>
            Choose a project...
          </option>
          {projects.map((project) => (
            <option key={project.id} value={project.name}>
              {project.name}
            </option>
          ))}
        </select>
        {/* Topic selector */}
        {selectedProject && (
          <select
            className={selectClass}
            id="topic-selector"
            value={selectedTopic?.title}
            onChange={(e) =>
              setSelectedTopic(topics.find((t) => t.title === e.target.value))
            }
          >
            <option value="">Choose a topic...</option>
            {topics.map((topic) => (
              <option key={topic.id} value={topic.title}>
                {topic.title}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Sentiment breakdown per topic */}
      {/* Pie chart showing posts' sentiment counts for selected topic */}
      {selectedTopic && sentimentCounts.length > 0 && (
        <div className={cardClass}>
          <h2 className="text-white text-lg font-semibold mb-4">
            Sentiment Breakdown — {selectedTopic.title}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentCounts}
                dataKey="count"
                nameKey="sentiment"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ sentiment, count }) => `${sentiment}: ${count}`}
              >
                {sentimentCounts.map((entry) => (
                  <Cell
                    key={`cell-${entry.sentiment}`}
                    fill={SENTIMENT_COLORS[entry.sentiment] || "#8884d8"}
                  />
                ))}
              </Pie>
              {/* <Tooltip contentStyle={tooltipStyle} /> */}
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Sentiment over time */}
      {/* Line chart showing sentiment trends across time for a topic */}
      {selectedTopic && sentimentTimeline.length > 0 && (
        <div className={cardClass}>
          <h2 className="text-white text-lg font-semibold mb-4">
            Sentiment Over Time — {selectedTopic.title}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[...sentimentTimeline]} width={500} height={300}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 13 }} />

              <Line
                type="monotone"
                dataKey="positive"
                stroke={SENTIMENT_COLORS.positive}
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="neutral"
                stroke={SENTIMENT_COLORS.neutral}
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="negative"
                stroke={SENTIMENT_COLORS.negative}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Experiment conversion rates */}
      {/* Bar chart comparing control vs. treatment conversion rates across experiments for a project */}
      {selectedProject && conversionRates.length > 0 && (
        <div className={cardClass}>
          <h2 className="text-white text-lg font-semibold mb-4">
            Experiment Conversion Rates
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={conversionRates}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3e" />
              <XAxis
                dataKey="title"
                stroke="#64748b"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fill: "#64748b", fontSize: 12 }}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 13 }} />
              <Bar dataKey="control" fill="#64748b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="treatment" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      {selectedTopic && sentimentCounts.length === 0 && (
        <p className="text-[#64748b]">No posts found for this topic yet.</p>
      )}
    </>
  );
}
export default Analytics;
