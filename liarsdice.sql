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
23	5	Lisa	1	4	0	{}	2017-11-13 14:56:44.709532	2017-11-13 14:56:44.709553
20	4	opponent_1	2	4	0	{}	2017-11-13 14:42:53.937475	2017-11-13 14:42:53.937548
22	4	opponent_3	4	\N	5	{2,6,4,4,1}	2017-11-13 14:42:53.939681	2017-11-13 14:42:53.9398
40	9	opponent_2	3	4	0	{}	2017-11-13 16:19:37.216192	2017-11-13 16:19:37.2162
19	4	Lisa	1	3	0	{6,4}	2017-11-13 14:42:53.93665	2017-11-13 14:42:53.936762
21	4	opponent_2	3	\N	0	{2}	2017-11-13 14:42:53.938602	2017-11-13 14:42:53.938667
33	7	opponent_3	4	5	0	{}	2017-11-13 15:19:15.176146	2017-11-13 15:19:15.176154
43	10	opponent_1	2	\N	5	{6,5,1,5,1}	2017-11-13 16:25:31.912074	2017-11-13 16:25:31.912163
16	3	opponent_3	4	6	0	{}	2017-11-13 12:23:06.42269	2017-11-13 12:23:06.422709
4	1	opponent_3	4	\N	1	{1,1,4}	2017-11-10 10:43:35.031549	2017-11-10 10:43:35.031613
37	8	opponent_3	4	4	0	{}	2017-11-13 15:52:58.844601	2017-11-13 15:52:58.844608
57	16	opponent_1	2	\N	5	{3,4,2,3,2}	2017-11-13 16:48:38.925468	2017-11-13 16:48:38.925505
42	10	Lisa	1	4	0	{3}	2017-11-13 16:25:31.910865	2017-11-13 16:25:31.911031
18	3	opponent_5	6	4	0	{}	2017-11-13 12:23:06.423245	2017-11-13 12:23:06.423259
14	3	opponent_1	2	\N	2	{4,2}	2017-11-13 12:23:06.422128	2017-11-13 12:23:06.422147
15	3	opponent_2	3	\N	2	{3,6}	2017-11-13 12:23:06.42242	2017-11-13 12:23:06.422439
13	3	Lisa	1	3	-1	{5}	2017-11-13 12:23:06.421841	2017-11-13 12:23:06.421873
60	18	Lisa	1	2	0	{5}	2017-11-13 16:52:38.59558	2017-11-13 16:52:38.5956
54	15	Lisa	1	2	0	{}	2017-11-13 16:46:48.600524	2017-11-13 16:46:48.600545
9	2	opponent_2	3	\N	4	{4,2,5,3}	2017-11-13 12:17:22.12782	2017-11-13 12:17:22.127884
10	2	opponent_3	4	\N	2	{6,3}	2017-11-13 12:17:22.128507	2017-11-13 12:17:22.128547
11	2	opponent_4	5	\N	5	{2,6,2,3,1}	2017-11-13 12:17:22.129234	2017-11-13 12:17:22.129276
12	2	opponent_5	6	\N	5	{5,1,1,4,6}	2017-11-13 12:17:22.129938	2017-11-13 12:17:22.129979
8	2	opponent_1	2	\N	2	{4,1}	2017-11-13 12:17:22.127016	2017-11-13 12:17:22.127055
7	2	Lisa	1	6	0	{}	2017-11-13 12:17:22.126414	2017-11-13 12:17:22.126486
47	11	opponent_1	2	\N	5	{2,5,2,6,3}	2017-11-13 16:28:52.479531	2017-11-13 16:28:52.479541
51	13	opponent_1	2	\N	5	{6,4,2,2,3}	2017-11-13 16:34:41.889852	2017-11-13 16:34:41.88986
5	1	opponent_4	5	\N	5	{4,2,1,6,5}	2017-11-10 10:43:35.034282	2017-11-10 10:43:35.034334
6	1	opponent_5	6	\N	5	{1,4,5,4,3}	2017-11-10 10:43:35.034838	2017-11-10 10:43:35.034871
46	11	Lisa	1	2	0	{2}	2017-11-13 16:28:52.479376	2017-11-13 16:28:52.479397
3	1	opponent_2	3	\N	2	{6,4}	2017-11-10 10:43:35.030734	2017-11-10 10:43:35.030773
2	1	opponent_1	2	\N	1	{3}	2017-11-10 10:43:35.030006	2017-11-10 10:43:35.030059
1	1	Lisa	1	6	0	{}	2017-11-10 10:43:35.029383	2017-11-10 10:43:35.029455
36	8	opponent_2	3	3	0	{}	2017-11-13 15:52:58.844485	2017-11-13 15:52:58.844493
55	15	opponent_1	2	\N	5	{4,6,1,3,3}	2017-11-13 16:46:48.600672	2017-11-13 16:46:48.600681
41	9	opponent_3	4	\N	3	{1,2,1}	2017-11-13 16:19:37.216308	2017-11-13 16:19:37.216315
29	6	opponent_3	4	\N	5	{3,5,4,5,4}	2017-11-13 15:04:46.488997	2017-11-13 15:04:46.489005
27	6	opponent_1	2	\N	4	{3,3,2,6}	2017-11-13 15:04:46.488705	2017-11-13 15:04:46.488714
26	6	Lisa	1	5	0	{}	2017-11-13 15:04:46.488529	2017-11-13 15:04:46.488553
34	8	Lisa	1	\N	5	{6,1,4,5,4}	2017-11-13 15:52:58.844155	2017-11-13 15:52:58.844174
28	6	opponent_2	3	\N	1	{2,5}	2017-11-13 15:04:46.488874	2017-11-13 15:04:46.488882
17	3	opponent_4	5	5	0	{}	2017-11-13 12:23:06.422988	2017-11-13 12:23:06.423008
39	9	opponent_1	2	\N	3	{6,6,5}	2017-11-13 16:19:37.216022	2017-11-13 16:19:37.21603
31	7	opponent_1	2	4	0	{}	2017-11-13 15:19:15.175847	2017-11-13 15:19:15.175856
25	5	opponent_2	3	\N	3	{3,4,6}	2017-11-13 14:56:44.709871	2017-11-13 14:56:44.709879
24	5	opponent_1	2	\N	3	{6,1,1}	2017-11-13 14:56:44.709677	2017-11-13 14:56:44.709686
35	8	opponent_1	2	2	0	{6}	2017-11-13 15:52:58.844297	2017-11-13 15:52:58.844306
30	7	Lisa	1	\N	1	{6}	2017-11-13 15:19:15.175691	2017-11-13 15:19:15.175712
32	7	opponent_2	3	3	0	{}	2017-11-13 15:19:15.176015	2017-11-13 15:19:15.176029
50	13	Lisa	1	2	0	{4}	2017-11-13 16:34:41.889704	2017-11-13 16:34:41.889724
38	9	Lisa	1	3	0	{3}	2017-11-13 16:19:37.215855	2017-11-13 16:19:37.215873
44	10	opponent_2	3	\N	5	{5,6,1,3,1}	2017-11-13 16:25:31.913265	2017-11-13 16:25:31.913333
45	10	opponent_3	4	\N	5	{4,4,4,5,4}	2017-11-13 16:25:31.91424	2017-11-13 16:25:31.914304
49	12	opponent_1	2	\N	5	{2,4,2,2,1}	2017-11-13 16:31:16.633332	2017-11-13 16:31:16.633341
48	12	Lisa	1	2	0	{6}	2017-11-13 16:31:16.633155	2017-11-13 16:31:16.633192
58	17	Lisa	1	2	0	{}	2017-11-13 16:51:27.89053	2017-11-13 16:51:27.890604
52	14	Lisa	1	\N	5	{5,4,3,3,2}	2017-11-13 16:36:28.550036	2017-11-13 16:36:28.550056
53	14	opponent_1	2	\N	5	{5,5,2,2,3}	2017-11-13 16:36:28.5502	2017-11-13 16:36:28.550209
61	18	opponent_1	2	\N	5	{1,1,2,3,2}	2017-11-13 16:52:38.595738	2017-11-13 16:52:38.595746
56	16	Lisa	1	2	0	{}	2017-11-13 16:48:38.924912	2017-11-13 16:48:38.924979
59	17	opponent_1	2	\N	5	{3,5,2,4,2}	2017-11-13 16:51:27.891187	2017-11-13 16:51:27.891225
63	19	opponent_1	2	\N	5	{5,1,1,6,4}	2017-11-13 16:53:58.82524	2017-11-13 16:53:58.825274
62	19	Lisa	1	2	0	{2}	2017-11-13 16:53:58.824679	2017-11-13 16:53:58.824753
\.


--
-- Name: abstract_players_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('abstract_players_id_seq', 63, true);


--
-- Data for Name: bids; Type: TABLE DATA; Schema: public; Owner: user
--

COPY bids (id, game_id, player_id, die_choice, die_count, created_at) FROM stdin;
474	6	28	2	2	2017-11-13 15:18:32.384734
475	6	29	5	3	2017-11-13 15:18:33.018234
476	6	27	3	4	2017-11-13 15:18:33.668195
477	6	28	2	5	2017-11-13 15:18:34.234227
706	10	42	2	17	2017-11-13 16:26:02.274244
711	11	46	2	10	2017-11-13 16:29:21.238994
716	12	48	2	11	2017-11-13 16:31:41.597262
721	13	50	2	14	2017-11-13 16:35:06.879807
742	18	60	2	12	2017-11-13 16:53:01.315257
747	19	62	2	11	2017-11-13 16:54:23.387983
643	8	35	6	1	2017-11-13 16:11:54.622028
644	8	34	6	3	2017-11-13 16:11:59.981832
699	9	39	6	1	2017-11-13 16:23:52.01204
700	9	41	2	2	2017-11-13 16:23:52.064981
701	9	38	3	7	2017-11-13 16:23:58.797135
645	8	35	6	4	2017-11-13 16:12:00.044176
\.


--
-- Name: bids_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('bids_id_seq', 747, true);


--
-- Data for Name: computers; Type: TABLE DATA; Schema: public; Owner: user
--

COPY computers (id, liar_factor, aggressive_factor, intelligence_factor) FROM stdin;
2	0.120999999999999996	0.52300000000000002	0.85199999999999998
3	0.149999999999999994	0.75	0.768000000000000016
4	0.14499999999999999	0.598999999999999977	0.777000000000000024
5	0.137000000000000011	0.540000000000000036	0.787000000000000033
6	0.107999999999999999	0.513000000000000012	0.830999999999999961
8	0.142999999999999988	0.594999999999999973	0.821999999999999953
9	0.149999999999999994	0.478999999999999981	0.809000000000000052
10	0.0980000000000000038	0.305999999999999994	0.821999999999999953
11	0.126000000000000001	0.68100000000000005	0.747999999999999998
12	0.111000000000000001	0.517000000000000015	0.803000000000000047
14	0.146999999999999992	0.461000000000000021	0.80600000000000005
15	0.131000000000000005	0.303999999999999992	0.819999999999999951
16	0.154999999999999999	0.808000000000000052	0.781000000000000028
17	0.106999999999999998	0.512000000000000011	0.807000000000000051
18	0.111000000000000001	0.362999999999999989	0.855999999999999983
20	0.151999999999999996	0.626000000000000001	0.812999999999999945
21	0.116000000000000006	0.385000000000000009	0.860999999999999988
22	0.102999999999999994	0.595999999999999974	0.803000000000000047
24	0.152999999999999997	0.464000000000000024	0.847999999999999976
25	0.109	0.47799999999999998	0.801000000000000045
27	0.146999999999999992	0.452000000000000013	0.733999999999999986
28	0.100000000000000006	0.836999999999999966	0.744999999999999996
29	0.0820000000000000034	0.598999999999999977	0.817999999999999949
31	0.190000000000000002	0.71599999999999997	0.778000000000000025
32	0.111000000000000001	0.576999999999999957	0.817999999999999949
33	0.121999999999999997	0.475999999999999979	0.82999999999999996
35	0.110000000000000001	0.424999999999999989	0.820999999999999952
36	0.119999999999999996	0.687999999999999945	0.804000000000000048
37	0.133000000000000007	0.559000000000000052	0.814999999999999947
39	0.104999999999999996	0.597999999999999976	0.747999999999999998
40	0.096000000000000002	0.405000000000000027	0.762000000000000011
41	0.133000000000000007	0.355999999999999983	0.846999999999999975
43	0.157000000000000001	0.654000000000000026	0.802000000000000046
44	0.123999999999999999	0.771000000000000019	0.810000000000000053
45	0.140999999999999986	0.668000000000000038	0.782000000000000028
47	0.106999999999999998	0.162000000000000005	0.809000000000000052
49	0.101999999999999993	0.740999999999999992	0.776000000000000023
51	0.129000000000000004	0.604999999999999982	0.808000000000000052
53	0.145999999999999991	0.583999999999999964	0.779000000000000026
55	0.096000000000000002	0.546000000000000041	0.776000000000000023
57	0.123999999999999999	0.653000000000000025	0.77200000000000002
59	0.145999999999999991	0.644000000000000017	0.807000000000000051
61	0.156	0.631000000000000005	0.820999999999999952
63	0.164000000000000007	0.673000000000000043	0.830999999999999961
\.


--
-- Data for Name: games; Type: TABLE DATA; Schema: public; Owner: user
--

COPY games (id, num_players, turn_marker, is_finished, difficulty, created_at, last_saved) FROM stdin;
14	2	2	f	h	2017-11-13 16:36:28.506154	2017-11-13 16:36:28.506179
1	6	1	f	h	2017-11-10 10:43:34.984011	2017-11-13 12:10:44.678383
3	6	2	f	h	2017-11-13 12:23:06.392505	2017-11-13 14:37:24.662017
9	4	2	f	h	2017-11-13 16:19:37.170038	2017-11-13 16:23:58.89869
8	4	1	t	h	2017-11-13 15:52:58.79733	2017-11-13 16:12:01.802784
5	3	2	f	h	2017-11-13 14:56:44.664723	2017-11-13 15:03:25.110725
15	2	2	t	h	2017-11-13 16:46:48.554505	2017-11-13 16:47:22.741894
10	4	2	f	h	2017-11-13 16:25:31.86379	2017-11-13 16:26:02.389131
4	4	3	f	h	2017-11-13 14:42:53.895938	2017-11-13 14:52:42.018605
16	2	2	t	h	2017-11-13 16:48:38.894563	2017-11-13 16:49:00.020145
7	4	1	f	h	2017-11-13 15:19:15.124455	2017-11-13 15:50:40.836573
11	2	2	t	h	2017-11-13 16:28:52.432863	2017-11-13 16:29:21.399658
17	2	2	t	h	2017-11-13 16:51:27.855675	2017-11-13 16:51:55.63199
12	2	2	t	h	2017-11-13 16:31:16.586337	2017-11-13 16:31:41.697003
6	4	3	f	h	2017-11-13 15:04:46.444379	2017-11-13 15:18:34.897939
2	6	2	f	h	2017-11-13 12:17:22.080985	2017-11-13 12:22:29.403835
18	2	2	t	h	2017-11-13 16:52:38.553257	2017-11-13 16:53:01.465657
13	2	2	t	h	2017-11-13 16:34:41.845762	2017-11-13 16:35:07.008428
19	2	2	t	h	2017-11-13 16:53:58.798772	2017-11-13 16:54:23.510471
\.


--
-- Name: games_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('games_id_seq', 19, true);


--
-- Data for Name: humans; Type: TABLE DATA; Schema: public; Owner: user
--

COPY humans (id, user_id) FROM stdin;
1	1
7	1
13	1
19	1
23	1
26	1
30	1
34	1
38	1
42	1
46	1
48	1
50	1
52	1
54	1
56	1
58	1
60	1
62	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--

COPY users (id, username, password, name, date_of_birth, created_at, last_login) FROM stdin;
1	lisamryl@gmail.com	test	Lisa	1986-02-16 00:00:00	2017-11-10 10:43:29.020056	2017-11-10 10:43:29.020093
2	l@gmail.com	test	Test	2000-01-21 00:00:00	2017-11-14 11:22:04.318812	2017-11-14 11:22:04.318839
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('users_id_seq', 2, true);


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

