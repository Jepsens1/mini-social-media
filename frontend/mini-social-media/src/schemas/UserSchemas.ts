import { CommentPublic } from "./CommentSchemas"
import { LikePublic } from "./LikeSchemas"
import { PostPublic } from "./PostSchemas"

export interface UserCreate {
    username: string
    password: string
    full_name?: string
}
export interface UserLogin {
    username: string
    password: string
}
export interface UserUpdate {
    username: string
    full_name?: string
}
export interface UserPublic {
    username: string
    is_active: boolean
    id: string
    created_at: string
    posts?: PostPublic[]
    comments?: CommentPublic[]
    likes: LikePublic[]
}