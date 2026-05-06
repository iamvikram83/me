import random

def get_unique_header(page_num, topic, age_group):
    """Generates unique instructions by mixing components dynamically."""
    is_junior = "6-9" in age_group
    
    if is_junior:
        actions = ["Explore the science of", "Observe the history of", "Analyze the structure of", "Imagine a future with", "Study the details of"]
        details = ["intricate patterns", "historical significance", "unique geometric shapes", "neon-ready outlines", "complex storytelling"]
        contexts = ["Focus on the precision of your lines.", "Use a palette that feels authentic.", "How would this look in 100 years?", "Add your own artistic flair to the background."]
    else:
        actions = ["Look at this happy", "Color the friendly", "Find the big", "Trace the lines of the", "Enjoy coloring this"]
        details = ["thick lines", "simple shapes", "smiling face", "bright spaces", "cheerful details"]
        contexts = ["Use your favorite bright colors!", "Stay inside the big lines.", "Draw a sun in the corner!", "Can you add some polka dots?"]

    # Use page_num as a seed to ensure the 'random' choice is consistent if the UI reruns
    random.seed(page_num)
    
    action = random.choice(actions)
    detail = random.choice(details)
    context = random.choice(contexts)
    
    return f"{action} {topic}. It has {detail}. {context}"
