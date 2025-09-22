import React from "react";
import { Post } from "../interfaces/Post";

interface PostCardProps {
  post: Post;
}

const PostCard = ({post}: PostCardProps) => {
  return (
    <div className="flex flex-col p-5 rounded-md bg-gray-800 text-green-500 w-full hover:bg-green-600 hover:text-white transition-all duration-300
    group">
      <h3 className="font-bold text-lg mb-1">{post.title}</h3>
      <p className="text-sm">{post.content}</p>

      <div className="text-xs text-gray-400 mt-auto group-hover:text-white">
        <p><span className="font-semibold">Likes:</span> {post.likes_count}</p>
        <p><span className="font-semibold">Kommentarer:</span> {post.comments_count}</p>
      </div>
      <div className="flex flex-col items-end text-[10px] text-gray-400 mt-auto group-hover:text-white">
        <p><span className="font-semibold">ID:</span> {post.id}</p>
        <p><span className="font-semibold">Created at:</span> {new Date(post.created_at).toLocaleString()}</p>
        {post.updated_at && (
          <p><span className="font-semibold">Last Edited:</span> {new Date(post.updated_at).toLocaleString()}</p>
        )}
      </div>
    </div>
  );
};

export default PostCard;
