export interface CommentCreate {
    content: string
}
export interface CommentPublic {
    id: string
    owner_id: string
    post_id: string
    created_at: string
    last_edited?: string
}
export interface CommentUpdate {
    content: string
}