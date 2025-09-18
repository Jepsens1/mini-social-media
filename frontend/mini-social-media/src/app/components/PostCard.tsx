import { PostPublic } from "@/schemas/PostSchemas";

export default async function PostCard({title, content}: PostPublic) {
    return (
        <div>
            <h1>{title}</h1>
            <h2>{content}</h2>
        </div>
    )
}