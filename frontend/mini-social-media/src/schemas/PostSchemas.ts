import { CommentPublic } from "./CommentSchemas"

export interface PostCreate {
    title: string
    content: string 
} 
export interface PostPublic {
    id: string
    title: string
    content: string
    owner_id: string
    created_at: string
    updated_at?: string
    likes_count: number
    comments_count: number
    comments?: CommentPublic[]
    liked_by?: string[]
}
export interface PostUpdate {
    title?: string
    content?: string 
}