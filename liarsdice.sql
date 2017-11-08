--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.9
-- Dumped by pg_dump version 9.5.9

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
-- Name: computers; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE computers (
    id integer NOT NULL,
    liar_factor double precision NOT NULL,
    aggressive_factor double precision NOT NULL,
    intelligence_factor double precision NOT NULL
);


ALTER TABLE computers OWNER TO vagrant;

--
-- Name: games; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE games (
    id integer NOT NULL,
    num_players integer NOT NULL,
    turn_marker integer NOT NULL,
    is_finished boolean NOT NULL,
    bid_history character varying(10)[],
    difficulty character varying(1) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    last_saved timestamp without time zone NOT NULL
);


ALTER TABLE games OWNER TO vagrant;

--
-- Name: games_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE games_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE games_id_seq OWNER TO vagrant;

--
-- Name: games_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE games_id_seq OWNED BY games.id;


--
-- Name: humans; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE humans (
    id integer NOT NULL,
    user_id integer
);


ALTER TABLE humans OWNER TO vagrant;

--
-- Name: players; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE players (
    id integer NOT NULL,
    game_id integer NOT NULL,
    name character varying(50) NOT NULL,
    "position" integer NOT NULL,
    final_place integer,
    die_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    last_played timestamp without time zone NOT NULL,
    current_die_roll integer[]
);


ALTER TABLE players OWNER TO vagrant;

--
-- Name: players_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE players_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE players_id_seq OWNER TO vagrant;

--
-- Name: players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE players_id_seq OWNED BY players.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: vagrant
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


ALTER TABLE users OWNER TO vagrant;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_id_seq OWNER TO vagrant;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY games ALTER COLUMN id SET DEFAULT nextval('games_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY players ALTER COLUMN id SET DEFAULT nextval('players_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Data for Name: computers; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY computers (id, liar_factor, aggressive_factor, intelligence_factor) FROM stdin;
2	0.086999999999999994	0.489999999999999991	0.765000000000000013
3	0.148999999999999994	0.426999999999999991	0.812999999999999945
4	0.0909999999999999976	0.387000000000000011	0.825999999999999956
5	0.130000000000000004	0.527000000000000024	0.700999999999999956
7	0.122999999999999998	0.418999999999999984	0.753000000000000003
8	0.151999999999999996	0.80600000000000005	0.762000000000000011
9	0.126000000000000001	0.565999999999999948	0.78400000000000003
10	0.120999999999999996	0.395000000000000018	0.841999999999999971
\.


--
-- Data for Name: games; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY games (id, num_players, turn_marker, is_finished, bid_history, difficulty, created_at, last_saved) FROM stdin;
1	5	3	f	\N	h	2017-11-07 23:21:12.769987	2017-11-07 23:21:12.770024
2	5	4	f	\N	h	2017-11-07 23:21:44.412866	2017-11-07 23:21:44.412896
\.


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('games_id_seq', 2, true);


--
-- Data for Name: humans; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY humans (id, user_id) FROM stdin;
1	1
6	1
\.


--
-- Data for Name: players; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY players (id, game_id, name, "position", final_place, die_count, created_at, last_played, current_die_roll) FROM stdin;
1	1	Lisa Casner	1	\N	5	2017-11-07 23:21:12.790219	2017-11-07 23:21:12.790293	\N
2	1	opponent_1	2	\N	5	2017-11-07 23:21:12.790431	2017-11-07 23:21:12.790444	\N
3	1	opponent_2	3	\N	5	2017-11-07 23:21:12.792025	2017-11-07 23:21:12.792045	\N
4	1	opponent_3	4	\N	5	2017-11-07 23:21:12.792185	2017-11-07 23:21:12.792197	\N
5	1	opponent_4	5	\N	5	2017-11-07 23:21:12.792417	2017-11-07 23:21:12.79243	\N
6	2	Lisa Casner	1	\N	5	2017-11-07 23:21:44.423837	2017-11-07 23:21:44.423865	\N
7	2	opponent_1	2	\N	5	2017-11-07 23:21:44.423984	2017-11-07 23:21:44.423996	\N
8	2	opponent_2	3	\N	5	2017-11-07 23:21:44.424194	2017-11-07 23:21:44.424243	\N
9	2	opponent_3	4	\N	5	2017-11-07 23:21:44.424374	2017-11-07 23:21:44.424386	\N
10	2	opponent_4	5	\N	5	2017-11-07 23:21:44.424506	2017-11-07 23:21:44.424517	\N
\.


--
-- Name: players_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('players_id_seq', 10, true);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY users (id, username, password, name, date_of_birth, created_at, last_login) FROM stdin;
1	lisamryl@gmail.com	test	Lisa Casner	1986-02-16 00:00:00	2017-11-07 23:20:37.992937	2017-11-07 23:20:37.99296
2	g@gmail.com	test	Test	1987-02-12 00:00:00	2017-11-07 23:24:38.024381	2017-11-07 23:24:38.024401
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('users_id_seq', 2, true);


--
-- Name: computers_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY computers
    ADD CONSTRAINT computers_pkey PRIMARY KEY (id);


--
-- Name: games_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_pkey PRIMARY KEY (id);


--
-- Name: humans_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY humans
    ADD CONSTRAINT humans_pkey PRIMARY KEY (id);


--
-- Name: players_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY players
    ADD CONSTRAINT players_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: computers_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY computers
    ADD CONSTRAINT computers_id_fkey FOREIGN KEY (id) REFERENCES players(id);


--
-- Name: humans_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY humans
    ADD CONSTRAINT humans_id_fkey FOREIGN KEY (id) REFERENCES players(id);


--
-- Name: humans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY humans
    ADD CONSTRAINT humans_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);


--
-- Name: players_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY players
    ADD CONSTRAINT players_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(id);


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

