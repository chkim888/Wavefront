from fastapi import APIRouter

# Router initialization
router = APIRouter(prefix="/topics")

## Create
# Create new topic (for a project)

# Create new keyword for a topic (for a topic)

# Create a new platform (general)

# Create post (for a keyword) -- add a field for associated keyword to posts?


## Read
# Read list of topics for a project

# Read list of keywords for a topic

# Read both topics and keywords for a project

# Read the list of available social media platforms

# Read list of posts for a keyword/topic/project


## Update
# Update topic title and/or description

# (updating keyword skipped -- just delete)

# Update platform information

# Update post sentiment label & score

## Delete
# Delete topic

# Delete keyword

# Delete platform

# Delete post