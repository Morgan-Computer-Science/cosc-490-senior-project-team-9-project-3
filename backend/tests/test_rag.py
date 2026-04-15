from app.rag import retrieve_relevant_documents


def test_retrieve_relevant_documents_supports_cloud_computing_queries():
    docs = retrieve_relevant_documents(
        "Help me plan cloud infrastructure and DevOps courses.",
        user_major="Cloud Computing",
        top_k=5,
    )

    assert docs
    assert any(
        (doc.major or "") == "Cloud Computing" or (doc.department or "") == "Cloud Computing"
        for doc in docs
    )


def test_retrieve_relevant_documents_supports_architecture_queries():
    docs = retrieve_relevant_documents(
        "What studio and building systems classes should I take next for architecture?",
        user_major="Architecture",
        top_k=5,
    )

    assert docs
    assert any(
        (doc.major or "") == "Architecture" or (doc.department or "") == "Architecture"
        for doc in docs
    )
