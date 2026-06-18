import authFetch from "./axios";

export const getAllTopics = async (projectId) => {
  try {
    // Send GET request to fetch all topics
    const res = await authFetch.get(`/topics/${projectId}`);
    return res.data;
  } catch (e) {
    console.log("Topics could not get fetched");
  }
};

export const getPostsForTopic = async (topicId) => {
  try {
    const res = await authFetch.get(`/topics/posts/${topicId}`);
    return res.data;
  } catch (e) {
    console.log("Posts could not get fetched");
  }
};

export const getKeywords = async (topicId) => {
  try {
    const res = await authFetch.get(`/topics/keywords/${topicId}`);
    return res.data;
  } catch (e) {
    console.log("Posts could not get fetched");
  }
};
