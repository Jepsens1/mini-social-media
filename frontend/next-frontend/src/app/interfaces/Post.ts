export interface Post {
  id: string;
  owner_id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string | null;
  likes_count: number;
  comments_count: number;
}

