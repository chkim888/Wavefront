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

  // triggered on page load to fetch all projects
  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getAllProjects();
        setProjects(res);
      } catch (e) {
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
        const res = await getAllTopics(selectedProject.id);
        setTopics(res);
        // reset for the new project
        setPosts([]);
        setSelectedTopic(null);
      } catch (e) {
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
        const res = await getPostsForTopic(selectedTopic.id);
        setPosts(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedTopic]);

  return (
    // JSX for the buzz monitor page
    <>
      {/* project selector */}
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

      {/* topic selector */}
      {selectedProject && (
        <select
          id="topic-select"
          value={selectedTopic?.title ?? ""}
          onChange={(e) =>
            setSelectedTopic(topics.find((t) => t.title === e.target.value))
          }
        >
          <option value="" disabled hidden>
            Choose a topic...
          </option>
          {topics.map((topic) => (
            <option key={topic.id} value={topic.title}>
              {topic.title}
            </option>
          ))}
        </select>
      )}

      {/* posts list */}
      {selectedTopic && (
        <ul>
          {posts.map((post) => (
            <li key={post.id}>
              <span>{post.content}</span>
              <span>{post.sentiment_label}</span>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
export default BuzzMonitor;
