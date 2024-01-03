--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1
-- Dumped by pg_dump version 16.1

-- Started on 2024-01-03 15:35:14 CST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3649 (class 1262 OID 16495)
-- Name: thoroughbred_api; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE thoroughbred_api WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';


ALTER DATABASE thoroughbred_api OWNER TO postgres;

\connect thoroughbred_api

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 16766)
-- Name: entry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entry (
    horse_id uuid NOT NULL,
    running_id uuid NOT NULL,
    jockey_id uuid,
    owner_id uuid,
    post_position integer,
    odds real,
    scratch boolean,
    past_turf_starts integer,
    past_turf_wins integer,
    past_polytrack_starts integer,
    past_polytrack_wins integer,
    last_raced date,
    last_raced_track_id uuid,
    last_raced_distance real,
    last_workout_track_id uuid,
    trainer_id uuid,
    last_raced_surface character varying(15)
);


ALTER TABLE public.entry OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16516)
-- Name: horse; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.horse (
    id uuid NOT NULL,
    name character varying(30) NOT NULL,
    sire_id uuid,
    owner_id uuid,
    trainer_id uuid
);


ALTER TABLE public.horse OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16731)
-- Name: jockey; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jockey (
    id uuid NOT NULL,
    first_name character varying(20),
    last_name character varying(30)
);


ALTER TABLE public.jockey OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16521)
-- Name: owner; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.owner (
    id uuid NOT NULL,
    name character varying(256)
);


ALTER TABLE public.owner OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16741)
-- Name: race; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.race (
    id uuid NOT NULL,
    track_id uuid,
    type character varying(15) NOT NULL,
    restriction character varying(15) NOT NULL,
    distance real NOT NULL,
    surface character varying(10) NOT NULL,
    name character varying(50),
    grade integer
);


ALTER TABLE public.race OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16751)
-- Name: running; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.running (
    id uuid NOT NULL,
    race_id uuid NOT NULL,
    date date NOT NULL,
    off_track boolean NOT NULL,
    half_mile_seconds real,
    final_seconds real,
    half_mile_winner_position real,
    winner_id uuid,
    num_on_day integer,
    field_size integer,
    meet character varying(15),
    winning_post integer
);


ALTER TABLE public.running OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16736)
-- Name: track; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.track (
    id uuid NOT NULL,
    abbreviation character varying(5) NOT NULL,
    name character varying(50),
    location character varying(60)
);


ALTER TABLE public.track OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16526)
-- Name: trainer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trainer (
    id uuid NOT NULL,
    first_name character varying(20),
    last_name character varying(30)
);


ALTER TABLE public.trainer OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16811)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id uuid NOT NULL,
    name character varying(15) NOT NULL,
    password character varying(256) NOT NULL,
    perms character varying(15) NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 3483 (class 2606 OID 16770)
-- Name: entry entry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_pkey PRIMARY KEY (horse_id, running_id);


--
-- TOC entry 3469 (class 2606 OID 16520)
-- Name: horse horse_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horse
    ADD CONSTRAINT horse_pkey PRIMARY KEY (id);


--
-- TOC entry 3475 (class 2606 OID 16735)
-- Name: jockey jockey_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jockey
    ADD CONSTRAINT jockey_pkey PRIMARY KEY (id);


--
-- TOC entry 3471 (class 2606 OID 16525)
-- Name: owner owner_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.owner
    ADD CONSTRAINT owner_pkey PRIMARY KEY (id);


--
-- TOC entry 3479 (class 2606 OID 16745)
-- Name: race race_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.race
    ADD CONSTRAINT race_pkey PRIMARY KEY (id);


--
-- TOC entry 3481 (class 2606 OID 16755)
-- Name: running running_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.running
    ADD CONSTRAINT running_pkey PRIMARY KEY (id);


--
-- TOC entry 3477 (class 2606 OID 16740)
-- Name: track track_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.track
    ADD CONSTRAINT track_pkey PRIMARY KEY (id);


--
-- TOC entry 3473 (class 2606 OID 16530)
-- Name: trainer trainer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trainer
    ADD CONSTRAINT trainer_pkey PRIMARY KEY (id);


--
-- TOC entry 3485 (class 2606 OID 16909)
-- Name: user user_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_name_key UNIQUE (name);


--
-- TOC entry 3487 (class 2606 OID 16815)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3494 (class 2606 OID 16771)
-- Name: entry entry_horse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_horse_id_fkey FOREIGN KEY (horse_id) REFERENCES public.horse(id);


--
-- TOC entry 3495 (class 2606 OID 16776)
-- Name: entry entry_jockey_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_jockey_id_fkey FOREIGN KEY (jockey_id) REFERENCES public.jockey(id);


--
-- TOC entry 3496 (class 2606 OID 16781)
-- Name: entry entry_last_raced_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_last_raced_track_id_fkey FOREIGN KEY (last_raced_track_id) REFERENCES public.track(id);


--
-- TOC entry 3497 (class 2606 OID 16786)
-- Name: entry entry_last_workout_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_last_workout_track_id_fkey FOREIGN KEY (last_workout_track_id) REFERENCES public.track(id);


--
-- TOC entry 3498 (class 2606 OID 16791)
-- Name: entry entry_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.owner(id);


--
-- TOC entry 3499 (class 2606 OID 16796)
-- Name: entry entry_running_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_running_id_fkey FOREIGN KEY (running_id) REFERENCES public.running(id);


--
-- TOC entry 3500 (class 2606 OID 16840)
-- Name: entry entry_trainer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entry
    ADD CONSTRAINT entry_trainer_id_fkey FOREIGN KEY (trainer_id) REFERENCES public.trainer(id);


--
-- TOC entry 3488 (class 2606 OID 16830)
-- Name: horse horse_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horse
    ADD CONSTRAINT horse_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.owner(id);


--
-- TOC entry 3489 (class 2606 OID 16820)
-- Name: horse horse_sire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horse
    ADD CONSTRAINT horse_sire_id_fkey FOREIGN KEY (sire_id) REFERENCES public.horse(id);


--
-- TOC entry 3490 (class 2606 OID 16825)
-- Name: horse horse_trainer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horse
    ADD CONSTRAINT horse_trainer_id_fkey FOREIGN KEY (trainer_id) REFERENCES public.trainer(id);


--
-- TOC entry 3491 (class 2606 OID 16746)
-- Name: race race_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.race
    ADD CONSTRAINT race_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.track(id);


--
-- TOC entry 3492 (class 2606 OID 16756)
-- Name: running running_race_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.running
    ADD CONSTRAINT running_race_id_fkey FOREIGN KEY (race_id) REFERENCES public.race(id);


--
-- TOC entry 3493 (class 2606 OID 16835)
-- Name: running running_winner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.running
    ADD CONSTRAINT running_winner_id_fkey FOREIGN KEY (winner_id) REFERENCES public.horse(id);


-- Completed on 2024-01-03 15:35:14 CST

--
-- PostgreSQL database dump complete
--

