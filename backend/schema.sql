CREATE TABLE users ( -- stores user information
	id UUID PRIMARY KEY,
	username VARCHAR(255) NOT NULL UNIQUE,
	email VARCHAR(255) UNIQUE NOT NULL,
	password_hash VARCHAR(255) NOT NULL, -- WILL NEED TO BE HASHED (bcrypt?)
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP -- useful for debugging or sorting
);

CREATE TABLE projects ( -- projects that monitor the same thing
	id UUID PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	description TEXT,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users_projects (
	user_id UUID,
	project_id UUID,
	PRIMARY KEY (user_id, project_id),
	role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'viewer')), -- two types of permissions possible
	FOREIGN KEY (user_id) REFERENCES users(id),
	FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE topics ( -- monitored topics (i.e. media type)
	id UUID PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	description TEXT NOT NULL,
	is_active BOOLEAN DEFAULT TRUE, -- for buzz monitoring
	project_id UUID NOT NULL, -- can belong to one project
	
	-- FOREIGN KEY
	CONSTRAINT fk_topics_project
		FOREIGN KEY (project_id)
		REFERENCES projects(id)
		ON DELETE CASCADE
);

CREATE TABLE keywords (
	id UUID PRIMARY KEY,
	topic_id UUID NOT NULL,
	project_id UUID NOT NULL,
	keyword VARCHAR(255) NOT NULL,
	UNIQUE (topic_id, keyword),
	
	-- FOREIGN KEYS
	CONSTRAINT fk_keywords_topic
		FOREIGN KEY (topic_id)
		REFERENCES topics(id)
		ON DELETE CASCADE,
	
	CONSTRAINT fk_keywords_project_id
		FOREIGN KEY (project_id)
		REFERENCES projects(id)
		ON DELETE CASCADE
);

CREATE TABLE platforms (
	id UUID PRIMARY KEY,
	name VARCHAR(255) NOT NULL
);

CREATE TABLE projects_platforms (
	project_id UUID,
	platform_id UUID,
	PRIMARY KEY (project_id, platform_id),
	FOREIGN KEY (project_id) REFERENCES projects(id),
	FOREIGN KEY (platform_id) REFERENCES platform(id)
);

CREATE TABLE posts ( -- streamlined event data
	id UUID PRIMARY KEY,
	external_id VARCHAR(255) NOT NULL,
	topic_id UUID NOT NULL,
	project_id UUID NOT NULL,
	platform_id UUID NOT NULL, -- name of the platform (i.e. reddit, twitter)
	original_poster VARCHAR(255) NOT NULL, -- ID of person who posted the content
	posted_time TIMESTAMP NOT NULL, -- time of posting
	content_type VARCHAR(255) NOT NULL CHECK (content_type IN ('post', 'comment', 'video')),
	content TEXT NOT NULL,	-- raw content in text
	view_count INTEGER,
	like_count INTEGER,
	comment_count INTEGER,
	sentiment_label VARCHAR(50) CHECK (sentiment_label IN ('positive', 'negative', 'neutral')),
	sentiment_score NUMERIC(4, 3),

	-- Foreign keys
	FOREIGN KEY (topic_id) REFERENCES topics(id),
	FOREIGN KEY (project_id) REFERENCES projects(id),

	CONSTRAINT uq_platform_external UNIQUE (platform_id, external_id),
	
	CONSTRAINT fk_posts_platform
		FOREIGN KEY (platform_id)
		REFERENCES platforms(id)
		ON DELETE CASCADE	
);

CREATE INDEX ix_posts_topic_id 
ON posts (topic_id);

CREATE TABLE alerts (
	id UUID PRIMARY KEY,
	project_id UUID NOT NULL,
	topic_id UUID NOT NULL,
	triggered_at TIMESTAMP NOT NULL,
	message TEXT

	CONSTRAINT fk_alerts_project
		FOREIGN KEY (project_id) 
		REFERENCES projects(id) 
		ON DELETE CASCADE,
	
	CONSTRAINT fk_alerts_topic
		FOREIGN KEY (topic_id) 
		REFERENCES topics(id) 
		ON DELETE CASCADE
);

CREATE INDEX ix_alerts_project_triggered 
ON alerts (project_id, triggered_at DESC);

CREATE TABLE experiments ( -- experiments for A/B testing
	id UUID PRIMARY KEY,
	project_id UUID NOT NULL,
	title VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL,
	curr_status VARCHAR(50) NOT NULL CHECK (curr_status IN ('created', 'running', 'complete', 'archived')),
	traffic_split INTEGER NOT NULL, -- store the side for treatment
	success_metric VARCHAR(50) NOT NULL, -- determine at app level & save info here (i.e. button click)
	start_time TIMESTAMP,
	end_time TIMESTAMP,
	
	-- FOREIGN KEYS
	CONSTRAINT fk_experiments_project
		FOREIGN KEY (project_id)
		REFERENCES projects(id)
		ON DELETE CASCADE
);

CREATE TABLE assignments (
	session_id VARCHAR(255) NOT NULL,
	experiment_id UUID NOT NULL,
	PRIMARY KEY (session_id, experiment_id),
	created_at TIMESTAMP NOT NULL,
	variant VARCHAR(255) NOT NULL CHECK (variant IN ('control', 'treatment')),
	
	-- FOREIGN KEY
	CONSTRAINT fk_assignments_experiment
		FOREIGN KEY (experiment_id)
		REFERENCES experiments(id)
		ON DELETE CASCADE
);

CREATE TABLE events (
	id UUID PRIMARY KEY,
	session_id VARCHAR(255) NOT NULL,
	experiment_id UUID NOT NULL,
	happened_at TIMESTAMP NOT NULL,
	event_type VARCHAR(255) NOT NULL, -- ex. button click
	
	-- FOREIGN KEY
	CONSTRAINT fk_events_experiment
		FOREIGN KEY (experiment_id)
		REFERENCES experiments(id)
		ON DELETE CASCADE
);

CREATE TABLE results (
	experiment_id UUID PRIMARY KEY,
	control_conversions INTEGER,
	treatment_conversions INTEGER,
	control_rate DOUBLE PRECISION,
	treatment_rate DOUBLE PRECISION
	lift DOUBLE PRECISION,
	confidence DOUBLE PRECISION,
	winner VARCHAR(50),
	
	-- FOREIGN KEY
	CONSTRAINT fk_results_experiment
		FOREIGN KEY (experiment_id)
		REFERENCES experiments(id)
		ON DELETE CASCADE
);