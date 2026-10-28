def optimize_text(raw_content):
    """
    CRITICAL: 100% Information Retention Rule.
    """
    shortened_log = []
    for point in raw_content:
        if length(point) > mobile_threshold:
            condense_phrasing_without_loss_of_meaning(point)
            shortened_log.append({"original": point, "optimized": new_point})
            
    print_to_user_stdout(shortened_log)
    return optimized_content