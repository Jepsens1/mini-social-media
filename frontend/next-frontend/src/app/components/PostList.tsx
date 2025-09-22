import React from 'react'
import PostCard from './PostCard'
import { Post } from '../interfaces/Post'

const PostList = async () => {
    const data = await fetch('http://localhost:8000/posts' , {cache: 'no-store'})
    const posts: Post[] = await data.json()
  return (
    <div className='bg-gray-50 grid gap-4 
      grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 p-4'>
        {posts.map((post) => (
            <PostCard key={post.id} post={post}/>
        ))}
    </div>
  )
}

export default PostList