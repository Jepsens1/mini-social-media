export interface User {
    id: string;
    username: string;
    full_name: string | null;
    is_active: boolean;
    created_at: string;
}