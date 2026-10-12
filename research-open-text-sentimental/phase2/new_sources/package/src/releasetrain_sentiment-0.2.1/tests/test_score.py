from releasetrain_sentiment import score_post, score_posts, trajectory_summary


def make_post():
    return {
        "title": "Update broke my build",
        "description": "Nothing compiles since 3.2.0",
        "comments": [
            {"text": "Known issue, fix coming soon", "author": "dev1", "is_author": True},
            {"text": "Same here, very annoying", "author": "user2", "is_author": False},
            {"text": "Thanks for the heads up", "author": "dev1", "is_author": True},
            {"text": "Still broken for me too", "author": "user3", "is_author": False},
        ],
    }


def test_score_post_returns_post_plus_one_item_per_comment():
    post = make_post()
    results = score_post(post)
    assert len(results) == len(post["comments"]) + 1


def test_first_item_is_the_post_itself():
    results = score_post(make_post())
    assert results[0]["source"] == "post"
    assert results[0]["index"] == -1
    assert results[0]["is_author"] is True


def test_comment_order_and_index_match_input():
    post = make_post()
    results = score_post(post)
    comment_results = results[1:]
    assert len(comment_results) == len(post["comments"])
    for i, (result, comment) in enumerate(zip(comment_results, post["comments"])):
        assert result["source"] == "comment"
        assert result["index"] == i
        assert result["is_author"] == comment["is_author"]


def test_each_item_has_a_sentiment_label():
    results = score_post(make_post())
    for item in results:
        assert item["label"] in ("Positive", "Negative", "Neutral")
        assert -1.0 <= item["compound"] <= 1.0


def test_empty_comments_list_returns_only_the_post():
    results = score_post({"title": "x", "description": "y", "comments": []})
    assert len(results) == 1
    assert results[0]["source"] == "post"


def test_score_posts_preserves_order_and_count():
    posts = [make_post(), make_post()]
    results = score_posts(posts)
    assert len(results) == 2
    assert all(len(r) == len(make_post()["comments"]) + 1 for r in results)


def test_trajectory_summary_separates_author_from_community():
    results = score_post(make_post())
    summary = trajectory_summary(results)
    assert "author_avg" in summary
    assert "community_avg" in summary
    assert "author_shift" in summary
    assert "community_shift" in summary


def test_trajectory_summary_handles_no_comments_of_one_kind():
    post = {
        "title": "x",
        "description": "y",
        "comments": [{"text": "only community here", "author": "u", "is_author": False}],
    }
    summary = trajectory_summary(score_post(post))
    assert summary["author_avg"] == 0.0
    assert summary["author_shift"] == 0.0
