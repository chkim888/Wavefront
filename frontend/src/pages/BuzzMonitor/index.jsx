import { getAllProjects } from "@/api/projects";
import { getAllTopics, getPostsForTopic } from "@/api/topics";
import { useEffect, useState } from "react";

function BuzzMonitor() {
  // set state variables
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);

  // triggered on page load to fetch all projects
  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true);
        const res = await getAllProjects();
        setProjects(res);
        setLoading(false);
      } catch (e) {
        setLoading(false);
        console.error(e);
      }
    };
    fetch();
  }, []);

  // triggered when selected project changes
  useEffect(() => {
    if (!selectedProject) return;
    const fetch = async () => {
      try {
        setLoading(true);
        const res = await getAllTopics(selectedProject.id);
        setTopics(res);
        setLoading(false);
      } catch (e) {
        setLoading(false);
        console.error(e);
      }
    };
    fetch();
  }, [selectedProject]);

  // similarly, triggered when selected topic changes
  useEffect(() => {
    if (!selectedTopic) return;
    const fetch = async () => {
      try {
        setLoading(true);
        const res = await getPostsForTopic(selectedTopic.id);
        setPosts(res);
        setLoading(false);
      } catch (e) {
        setLoading(false);
        console.error(e);
      }
    };
    fetch();
  }, [selectedTopic]);

  return (
    // JSX for the buzz monitor page
    <>
      {/* loading page */}
      {loading && <h1>Loading...</h1>}
      
      {/* project selector */}
      <select
        id="project-select"
        value={selectedProject?.name ?? ""}
        onChange={(e) =>
          setSelectedProject(projects.find((p) => p.name === e.target.value))
        }
      >
        {projects.map((project) => (
          <option key={project.id} value={project.name}>
            {project.name}
          </option>
        ))}
      </select>

      {/* topic selector */}
      {selectedProject && (
        <select
          id="topic-select"
          value={selectedTopic?.name ?? ""}
          onChange={(e) =>
            setSelectedTopic(topics.find((t) => t.title === e.target.value))
          }
        >
          {topics.map((topic) => (
            <option key={topic.id} value={topic.title}>
              {topic.title}
            </option>
          ))}
        </select>
      )}

      {/* posts list */}
      {selectedTopic && (
        <div>
          {posts.map((post) => (
            <li key={post.id}>
              <span>{post.content}</span>
              <span>{post.sentiment_label}</span>
            </li>
          ))}
        </div>
      )}
    </>
  );
}
export default BuzzMonitor;
