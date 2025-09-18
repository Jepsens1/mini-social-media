import PostCard from "./PostCard"

export default async function PostList() {
    const data = await fetch('https://api.vercel.app/blog')
    const posts = await data.json()

    return (
        <>
            {posts.map((post) => (
                <PostCard key={post.id} title={post.title} content={post.content}/>
            ))}
        </>
    )
}