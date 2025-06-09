-- Function to find top k similar memories using cosine similarity
CREATE OR REPLACE FUNCTION find_similar_memories(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.3,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id integer,
    conv_id integer,
    ques_analysis text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        notion_embedding.id,
        notion_embedding.conv_id,
        notion_embedding.ques_analysis,
        1 - (notion_embedding.embedding <=> query_embedding) as similarity
    FROM notion_embedding
    WHERE 1 - (notion_embedding.embedding <=> query_embedding) > similarity_threshold
    ORDER BY notion_embedding.embedding <=> query_embedding
    LIMIT match_count;
END;
$$; 