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
  const COLORS = {
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

  // JSX
  return (
    <>
      {/* Project selector */}
      <select
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

      {/* Sentiment breakdown per topic */}
      {/* Pie chart showing posts' sentiment counts for selected topic */}
      {selectedTopic && (
        <PieChart width={400} height={400}>
          <Pie
            data={sentimentCounts}
            dataKey="count"
            nameKey="sentiment"
            label={({ sentiment, count }) => `${sentiment}: ${count}`}
          >
            {sentimentCounts.map((entry) => (
              <Cell
                key={`cell-${entry.sentiment}`}
                fill={COLORS[entry.sentiment] || "#8884d8"}
              />
            ))}
          </Pie>
          <Legend />
        </PieChart>
      )}

      {/* Sentiment over time */}
      {/* Line chart showing sentiment trends across time for a topic */}
      {selectedTopic && (
        <LineChart data={[...sentimentTimeline]} width={500} height={300}>
          <XAxis dataKey="date" />
          <YAxis />
          <Legend />
          <Line
            dataKey="positive"
            stroke="#22c55e"
            strokeWidth={2}
            name="Positive"
          />
          <Line
            dataKey="neutral"
            stroke="#94a3b8"
            strokeWidth={2}
            name="Neutral"
          />
          <Line
            dataKey="negative"
            stroke="#ef4444"
            strokeWidth={2}
            name="Negative"
          />
        </LineChart>
      )}

      {/* Experiment conversion rates */}
      {/* Bar chart comparing control vs. treatment conversion rates across experiments for a project */}
      {selectedProject && (
        <BarChart data={conversionRates} width={500} height={300}>
          <XAxis dataKey="title" />
          <YAxis />
          <Legend />
          <Bar dataKey="control" fill="#AEC6CF" name="Control" />
          <Bar dataKey="treatment" fill="#CFB7AE" name="Treatment" />
        </BarChart>
      )}
    </>
  );
}
export default Analytics;
