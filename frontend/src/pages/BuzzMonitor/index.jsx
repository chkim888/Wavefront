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
      <h1 className="text-white text-2xl font-bold mb-6">Buzz Monitor</h1>
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        {/* project selector */}
        <select
          className="bg-[#1e2130] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 w-full md:w-auto"
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
            className="bg-[#1e2130] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 w-full md:w-auto"
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
      </div>

      {/* posts list */}
      {selectedTopic && (
        <ul>
          {posts.map((post) => (
            <li
              key={post.id}
              className="bg-[#1e2130] border border-[#2a2d3e] rounded-lg p-4 mb-3"
            >
              <div className="flex justify-between items-center">
                <span>{post.content}</span>
                <span
                  className={
                    post.sentiment_label === "positive"
                      ? "text-green-400"
                      : post.sentiment_label === "negative"
                        ? "text-red-400"
                        : "text-gray-400"
                  }
                >
                  {post.sentiment_label}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
export default BuzzMonitor;
