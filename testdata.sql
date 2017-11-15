--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.8
-- Dumped by pg_dump version 9.5.8

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: abstract_players; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE abstract_players (
    id integer NOT NULL,
    game_id integer NOT NULL,
    name character varying(50) NOT NULL,
    "position" integer NOT NULL,
    final_place integer,
    die_count integer NOT NULL,
    current_die_roll integer[],
    created_at timestamp without time zone NOT NULL,
    last_played timestamp without time zone NOT NULL
);


ALTER TABLE abstract_players OWNER TO "user";

--
-- Name: abstract_players_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE abstract_players_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE abstract_players_id_seq OWNER TO "user";

--
-- Name: abstract_players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE abstract_players_id_seq OWNED BY abstract_players.id;


--
-- Name: bids; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE bids (
    id integer NOT NULL,
    game_id integer NOT NULL,
    player_id integer NOT NULL,
    die_choice integer NOT NULL,
    die_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE bids OWNER TO "user";

--
-- Name: bids_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE bids_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE bids_id_seq OWNER TO "user";

--
-- Name: bids_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE bids_id_seq OWNED BY bids.id;


--
-- Name: computers; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE computers (
    id integer NOT NULL,
    liar_factor double precision NOT NULL,
    aggressive_factor double precision NOT NULL,
    intelligence_factor double precision NOT NULL
);


ALTER TABLE computers OWNER TO "user";

--
-- Name: games; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE games (
    id integer NOT NULL,
    num_players integer NOT NULL,
    turn_marker integer NOT NULL,
    is_finished boolean NOT NULL,
    difficulty character varying(1) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    last_saved timestamp without time zone NOT NULL
);


ALTER TABLE games OWNER TO "user";

--
-- Name: games_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE games_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE games_id_seq OWNER TO "user";

--
-- Name: games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE games_id_seq OWNED BY games.id;


--
-- Name: humans; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE humans (
    id integer NOT NULL,
    user_id integer
);


ALTER TABLE humans OWNER TO "user";

--
-- Name: users; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    password character varying(64) NOT NULL,
    name character varying(64) NOT NULL,
    date_of_birth timestamp without time zone NOT NULL,
    created_at timestamp without time zone NOT NULL,
    last_login timestamp without time zone NOT NULL
);


ALTER TABLE users OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_id_seq OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY abstract_players ALTER COLUMN id SET DEFAULT nextval('abstract_players_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY bids ALTER COLUMN id SET DEFAULT nextval('bids_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY games ALTER COLUMN id SET DEFAULT nextval('games_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Data for Name: abstract_players; Type: TABLE DATA; Schema: public; Owner: user
--

COPY abstract_players (id, game_id, name, "position", final_place, die_count, current_die_roll, created_at, last_played) FROM stdin;
1	1	Test	1	\N	3	{1,1,5}	2017-11-14 11:43:03.898887	2017-11-14 11:43:03.89896
2	1	opponent_1	2	\N	4	{6,6,2,5}	2017-11-14 11:43:03.899558	2017-11-14 11:43:03.8996
3	1	opponent_2	3	\N	5	{3,2,6,2,5}	2017-11-14 11:43:03.900278	2017-11-14 11:43:03.900317
4	1	opponent_3	4	\N	5	{2,1,6,6,4}	2017-11-14 11:43:03.900807	2017-11-14 11:43:03.900842
\.


--
-- Name: abstract_players_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('abstract_players_id_seq', 4, true);


--
-- Data for Name: bids; Type: TABLE DATA; Schema: public; Owner: user
--

COPY bids (id, game_id, player_id, die_choice, die_count, created_at) FROM stdin;
\.


--
-- Name: bids_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('bids_id_seq', 24, true);


--
-- Data for Name: computers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY computers (id, liar_factor, aggressive_factor, intelligence_factor) FROM stdin;
2	0.131000000000000005	0.64800000000000002	0.826999999999999957
3	0.140000000000000013	0.596999999999999975	0.778000000000000025
4	0.16800000000000001	0.539000000000000035	0.781000000000000028
\.


--
-- Data for Name: games; Type: TABLE DATA; Schema: public; Owner: user
--

COPY games (id, num_players, turn_marker, is_finished, difficulty, created_at, last_saved) FROM stdin;
1	4	2	f	h	2017-11-14 11:43:03.856637	2017-11-14 11:44:24.251038
\.


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('games_id_seq', 1, true);


--
-- Data for Name: humans; Type: TABLE DATA; Schema: public; Owner: user
--

COPY humans (id, user_id) FROM stdin;
1	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--

COPY users (id, username, password, name, date_of_birth, created_at, last_login) FROM stdin;
1	l@gmail.com	test	Test	2000-01-01 00:00:00	2017-11-14 11:42:56.344832	2017-11-14 11:42:56.344855
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('users_id_seq', 1, true);


--
-- Name: abstract_players_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY abstract_players
    ADD CONSTRAINT abstract_players_pkey PRIMARY KEY (id);


--
-- Name: bids_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY bids
    ADD CONSTRAINT bids_pkey PRIMARY KEY (id);


--
-- Name: computers_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY computers
    ADD CONSTRAINT computers_pkey PRIMARY KEY (id);


--
-- Name: games_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: humans_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY humans
    ADD CONSTRAINT humans_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: abstract_players_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY abstract_players
    ADD CONSTRAINT abstract_players_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(id);


--
-- Name: bids_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY bids
    ADD CONSTRAINT bids_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(id);


--
-- Name: bids_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY bids
    ADD CONSTRAINT bids_player_id_fkey FOREIGN KEY (player_id) REFERENCES abstract_players(id);


--
-- Name: computers_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY computers
    ADD CONSTRAINT computers_id_fkey FOREIGN KEY (id) REFERENCES abstract_players(id);


--
-- Name: humans_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY humans
    ADD CONSTRAINT humans_id_fkey FOREIGN KEY (id) REFERENCES abstract_players(id);


--
-- Name: humans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY humans
    ADD CONSTRAINT humans_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

