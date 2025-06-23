from create_database import get_chroma_session

def query(user_request: str = "What is the latest news?", collection_id: str = None):
    """
    Query a specific ChromaDB collection for relevant documents
    Args:
        user_request: The search query
        collection_id: The ID of the collection to search in
    """
    if collection_id is None:
        print("No collection ID provided")
        return None
        
    # Get the specific collection
    db, _ = get_chroma_session(collection_id)

    results = db.similarity_search_with_relevance_scores(user_request, k=5)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return
    
    #print result one by one
    for doc, score in results:
        print(f"Score: {score:.4f}")
        print(f"Content: {doc.page_content}")


    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    return context_text
