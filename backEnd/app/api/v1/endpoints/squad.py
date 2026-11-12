from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.core.database import get_db
from app.models.squad import Player
from app.schemas.squad import (
    PlayerResponse,
    PlayerDetailResponse,
    PlayerComparisonResponse,
    PlayerComparisonItem
)

router = APIRouter()

DEPARTED_PLAYER_IDS = (
    "ply_neto",
    "ply_sterling",
    "ply_zinchenko",
    "ply_tomiyasu",
    "ply_kiwior",
    "ply_partey",
    "ply_jorginho",
)

# Official Arsenal FC Men's First-Team Squad
DEFAULT_PLAYERS: List[dict] = [
    # Goalkeepers
    {
        "id": "ply_raya",
        "club_id": "arsenal",
        "name": "David Raya",
        "short_name": "D. Raya",
        "position": "Goalkeeper",
        "jersey_number": 1,
        "nationality": "Spain",
        "appearances": 38,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 16,
        "minutes_played": 3420,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/5a548482772b-arsenalmenssquad26271david-raya.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/5a548482772b-arsenalmenssquad26271david-raya.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-david-raya-action.jpg",
        "bio": "Commanding modern sweeper-keeper and Premier League Golden Glove winner. Raya anchors Arsenal's build-up under high pressure with pinpoint distribution and fearless high-claim authority on set pieces.",
        "date_of_birth": "1995-09-15",
        "height": "183 cm",
        "joined_date": "August 2023",
    },
    {
        "id": "ply_kepa",
        "club_id": "arsenal",
        "name": "Kepa Arrizabalaga",
        "short_name": "Kepa",
        "position": "Goalkeeper",
        "jersey_number": 13,
        "nationality": "Spain",
        "appearances": 9,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 5,
        "minutes_played": 810,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-kepa-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-kepa-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-kepa-action.jpg",
        "bio": "Experienced Spanish international shot-stopper brought in to fortify cup and continental rotation. Renowned for sharp close-range reflexes, penalty-shootout composure, and calm ball-playing feet.",
        "date_of_birth": "1994-10-03",
        "height": "189 cm",
        "joined_date": "July 2025",
    },
    {
        "id": "ply_setford",
        "club_id": "arsenal",
        "name": "Tommy Setford",
        "short_name": "T. Setford",
        "position": "Goalkeeper",
        "jersey_number": 35,
        "nationality": "England",
        "appearances": 2,
        "goals": 0,
        "assists": 0,
        "clean_sheets": 1,
        "minutes_played": 180,
        "yellow_cards": 0,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-tommy-setford-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-tommy-setford-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-tommy-setford-action.jpg",
        "bio": "England youth international graduate trained in Ajax's possession school before arriving in North London. Combines long reach with fearless line-breaking passing from the penalty box.",
        "date_of_birth": "2006-03-13",
        "height": "188 cm",
        "joined_date": "July 2024",
    },
    # Defenders
    {
        "id": "ply_saliba",
        "club_id": "arsenal",
        "name": "William Saliba",
        "short_name": "W. Saliba",
        "position": "Defender",
        "jersey_number": 2,
        "nationality": "France",
        "appearances": 36,
        "goals": 2,
        "assists": 1,
        "clean_sheets": 15,
        "minutes_played": 3210,
        "yellow_cards": 3,
        "red_cards": 1,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-william-saliba-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-william-saliba-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-william-saliba-action.jpg",
        "bio": "Rolls-Royce right-sided centre-back whose recovery pace, 1v1 channel defending, and press-resistant first touch allow Arsenal to squeeze the defensive line to the halfway mark.",
        "date_of_birth": "2001-03-24",
        "height": "192 cm",
        "joined_date": "July 2019",
    },
    {
        "id": "ply_mosquera",
        "club_id": "arsenal",
        "name": "Cristhian Mosquera",
        "short_name": "C. Mosquera",
        "position": "Defender",
        "jersey_number": 3,
        "nationality": "Spain",
        "appearances": 16,
        "goals": 0,
        "assists": 1,
        "clean_sheets": 7,
        "minutes_played": 1240,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-cristhian-mosquera-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-cristhian-mosquera-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-cristhian-mosquera-action.jpg",
        "bio": "Athletic young Spanish centre-back recruited from Valencia to provide elite right-centre and hybrid full-back cover. Excels at front-foot interceptions and defending wide spaces.",
        "date_of_birth": "2004-06-27",
        "height": "191 cm",
        "joined_date": "July 2025",
    },
    {
        "id": "ply_white",
        "club_id": "arsenal",
        "name": "Ben White",
        "short_name": "B. White",
        "position": "Defender",
        "jersey_number": 4,
        "nationality": "England",
        "appearances": 28,
        "goals": 2,
        "assists": 4,
        "clean_sheets": 11,
        "minutes_played": 2340,
        "yellow_cards": 4,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-ben-white-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-ben-white-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-ben-white-action.jpg",
        "bio": "Relentless overlapping and underlapping right-back whose chemistry with Bukayo Saka and Martin Ødegaard drives Arsenal's right-flank dominance and near-post set-piece disruption.",
        "date_of_birth": "1997-10-08",
        "height": "186 cm",
        "joined_date": "July 2021",
    },
    {
        "id": "ply_hincapie",
        "club_id": "arsenal",
        "name": "Piero Hincapié",
        "short_name": "P. Hincapié",
        "position": "Defender",
        "jersey_number": 5,
        "nationality": "Ecuador",
        "appearances": 21,
        "goals": 1,
        "assists": 2,
        "clean_sheets": 9,
        "minutes_played": 1690,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-piero-hincapie-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-piero-hincapie-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-piero-hincapie-action.jpg",
        "bio": "Left-footed Ecuadorian international equally comfortable at left centre-back or tucked-in left-back. Brings Bundesliga-proven aggression, progressive carrying, and aerial bite.",
        "date_of_birth": "2002-01-09",
        "height": "184 cm",
        "joined_date": "September 2025",
    },
    {
        "id": "ply_gabriel",
        "club_id": "arsenal",
        "name": "Gabriel Magalhães",
        "short_name": "Gabriel",
        "position": "Defender",
        "jersey_number": 6,
        "nationality": "Brazil",
        "appearances": 35,
        "goals": 5,
        "assists": 1,
        "clean_sheets": 15,
        "minutes_played": 3100,
        "yellow_cards": 5,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-gabriel-magalhaes-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-gabriel-magalhaes-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-gabriel-magalhaes-action.jpg",
        "bio": "Warrior leader of the Arsenal back four and Europe's premier set-piece attacking threat. Dominates physical duels in both penalty areas while organizing the defensive line.",
        "date_of_birth": "1997-12-19",
        "height": "190 cm",
        "joined_date": "September 2020",
    },
    {
        "id": "ply_timber",
        "club_id": "arsenal",
        "name": "Jurriën Timber",
        "short_name": "J. Timber",
        "position": "Defender",
        "jersey_number": 12,
        "nationality": "Netherlands",
        "appearances": 34,
        "goals": 2,
        "assists": 4,
        "clean_sheets": 13,
        "minutes_played": 2760,
        "yellow_cards": 4,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-jurrien-timber-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-jurrien-timber-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-jurrien-timber-action.jpg",
        "bio": "Tactically ambidextrous full-back capable of locking down elite wingers on either flank. Inverted movement into midfield gives Arsenal effortless numerical superiority in build-up.",
        "date_of_birth": "2001-06-17",
        "height": "179 cm",
        "joined_date": "July 2023",
    },
    {
        "id": "ply_calafiori",
        "club_id": "arsenal",
        "name": "Riccardo Calafiori",
        "short_name": "R. Calafiori",
        "position": "Defender",
        "jersey_number": 33,
        "nationality": "Italy",
        "appearances": 25,
        "goals": 2,
        "assists": 3,
        "clean_sheets": 9,
        "minutes_played": 1820,
        "yellow_cards": 4,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-riccardo-calafiori-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-riccardo-calafiori-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-riccardo-calafiori-action.jpg",
        "bio": "Free-roaming Italian left-back who surges effortlessly from deep into the left half-space. Combines strong aerial timing with thunderous ball-striking from the edge of the box.",
        "date_of_birth": "2002-05-19",
        "height": "188 cm",
        "joined_date": "July 2024",
    },
    {
        "id": "ply_lewis_skelly",
        "club_id": "arsenal",
        "name": "Myles Lewis-Skelly",
        "short_name": "M. Lewis-Skelly",
        "position": "Defender",
        "jersey_number": 49,
        "nationality": "England",
        "appearances": 27,
        "goals": 2,
        "assists": 4,
        "clean_sheets": 10,
        "minutes_played": 2050,
        "yellow_cards": 3,
        "red_cards": 1,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-myles-lewis-skelly-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-myles-lewis-skelly-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-myles-lewis-skelly-action.jpg",
        "bio": "Hale End sensation transformed into an inverted left-back dynamo. Uses low-centre-of-gravity shielding and press-resistant turns to break opposition traps and drive through midfield.",
        "date_of_birth": "2006-09-26",
        "height": "178 cm",
        "joined_date": "July 2024 (Hale End)",
    },
    # Midfielders
    {
        "id": "ply_odegaard",
        "club_id": "arsenal",
        "name": "Martin Ødegaard",
        "short_name": "M. Ødegaard",
        "position": "Midfielder",
        "jersey_number": 8,
        "nationality": "Norway",
        "appearances": 32,
        "goals": 8,
        "assists": 11,
        "clean_sheets": 0,
        "minutes_played": 2690,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-martin-odegaard-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-martin-odegaard-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-martin-odegaard-action.jpg",
        "bio": "Club captain and creative metronome. Orchestrates Arsenal's first-line press while threading disguised reverse passes into the right half-space and penalty box.",
        "date_of_birth": "1998-12-17",
        "height": "178 cm",
        "joined_date": "August 2021",
    },
    {
        "id": "ply_eze",
        "club_id": "arsenal",
        "name": "Eberechi Eze",
        "short_name": "E. Eze",
        "position": "Midfielder",
        "jersey_number": 10,
        "nationality": "England",
        "appearances": 26,
        "goals": 8,
        "assists": 7,
        "clean_sheets": 0,
        "minutes_played": 2040,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-eberechi-eze-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-eberechi-eze-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-eberechi-eze-action.jpg",
        "bio": "Silk-footed No. 10 who glides past compact mid-blocks in tight central pockets. Adds unpredictable ball-carrying, dead-ball precision, and goal threat from the left half-space.",
        "date_of_birth": "1998-06-29",
        "height": "178 cm",
        "joined_date": "August 2025",
    },
    {
        "id": "ply_norgaard",
        "club_id": "arsenal",
        "name": "Christian Nørgaard",
        "short_name": "C. Nørgaard",
        "position": "Midfielder",
        "jersey_number": 16,
        "nationality": "Denmark",
        "appearances": 15,
        "goals": 1,
        "assists": 2,
        "clean_sheets": 0,
        "minutes_played": 960,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-christian-norgaard-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-christian-norgaard-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-christian-norgaard-action.jpg",
        "bio": "Disciplined Danish holding midfielder and tactical anchor for closing out high-stakes fixtures. Shields the back line with positional intelligence and crisp one-touch recycling.",
        "date_of_birth": "1994-03-10",
        "height": "187 cm",
        "joined_date": "July 2025",
    },
    {
        "id": "ply_nwaneri",
        "club_id": "arsenal",
        "name": "Ethan Nwaneri",
        "short_name": "E. Nwaneri",
        "position": "Midfielder",
        "jersey_number": 22,
        "nationality": "England",
        "appearances": 24,
        "goals": 6,
        "assists": 3,
        "clean_sheets": 0,
        "minutes_played": 1190,
        "yellow_cards": 1,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-ethan-nwaneri-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-ethan-nwaneri-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-ethan-nwaneri-action.jpg",
        "bio": "Hale End prodigy and the youngest player in Premier League history. Cuts inside off the right half-space onto a razor-sharp left foot capable of curling shots from distance.",
        "date_of_birth": "2007-03-21",
        "height": "176 cm",
        "joined_date": "July 2024 (Hale End)",
    },
    {
        "id": "ply_merino",
        "club_id": "arsenal",
        "name": "Mikel Merino",
        "short_name": "M. Merino",
        "position": "Midfielder",
        "jersey_number": 23,
        "nationality": "Spain",
        "appearances": 29,
        "goals": 6,
        "assists": 3,
        "clean_sheets": 0,
        "minutes_played": 1940,
        "yellow_cards": 4,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-mikel-merino-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-mikel-merino-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-mikel-merino-action.jpg",
        "bio": "Euro-winning Spanish duel-monster whose aerial supremacy, counter-pressing instincts, and late box-crashing runs make him a dual threat in midfield and emergency striker roles.",
        "date_of_birth": "1996-06-22",
        "height": "189 cm",
        "joined_date": "August 2024",
    },
    {
        "id": "ply_zubimendi",
        "club_id": "arsenal",
        "name": "Martín Zubimendi",
        "short_name": "M. Zubimendi",
        "position": "Midfielder",
        "jersey_number": 36,
        "nationality": "Spain",
        "appearances": 31,
        "goals": 2,
        "assists": 4,
        "clean_sheets": 0,
        "minutes_played": 2610,
        "yellow_cards": 4,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-martin-zubimendi-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-martin-zubimendi-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-martin-zubimendi-action.jpg",
        "bio": "Cerebral Basque No. 6 recruited to dictate build-up tempo from deep. Reads opposition pressing traps before receiving, unlocking Declan Rice to surge higher up the pitch.",
        "date_of_birth": "1999-02-02",
        "height": "181 cm",
        "joined_date": "July 2025",
    },
    {
        "id": "ply_rice",
        "club_id": "arsenal",
        "name": "Declan Rice",
        "short_name": "D. Rice",
        "position": "Midfielder",
        "jersey_number": 41,
        "nationality": "England",
        "appearances": 37,
        "goals": 6,
        "assists": 7,
        "clean_sheets": 0,
        "minutes_played": 3240,
        "yellow_cards": 4,
        "red_cards": 1,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-declan-rice-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-declan-rice-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-declan-rice-action.jpg",
        "bio": "Relentless midfield powerhouse combining elite transition ball-winning with sweeping box-to-box surges, whipped corner deliveries, and decisive big-game strikes.",
        "date_of_birth": "1999-01-14",
        "height": "188 cm",
        "joined_date": "July 2023",
    },
    # Attackers / Forwards
    {
        "id": "ply_saka",
        "club_id": "arsenal",
        "name": "Bukayo Saka",
        "short_name": "B. Saka",
        "position": "Attacker",
        "jersey_number": 7,
        "nationality": "England",
        "appearances": 34,
        "goals": 14,
        "assists": 13,
        "clean_sheets": 0,
        "minutes_played": 2890,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-bukayo-saka-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-bukayo-saka-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-bukayo-saka-action.jpg",
        "bio": "Arsenal's talismanic Starboy and Hale End standard-bearer. Routinely beats double-teams on the right touchline to deliver curlers into the far corner or pinpoint in-swinging crosses.",
        "date_of_birth": "2001-09-05",
        "height": "178 cm",
        "joined_date": "July 2018 (Hale End)",
    },
    {
        "id": "ply_jesus",
        "club_id": "arsenal",
        "name": "Gabriel Jesus",
        "short_name": "G. Jesus",
        "position": "Attacker",
        "jersey_number": 9,
        "nationality": "Brazil",
        "appearances": 20,
        "goals": 5,
        "assists": 3,
        "clean_sheets": 0,
        "minutes_played": 1140,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-gabriel-jesus-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-gabriel-jesus-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-gabriel-jesus-action.jpg",
        "bio": "Electric Brazilian forward whose close control in congested penalty areas, tireless pressing energy, and Champions League knockout pedigree elevate Arsenal's attacking fluidity.",
        "date_of_birth": "1997-04-03",
        "height": "175 cm",
        "joined_date": "July 2022",
    },
    {
        "id": "ply_martinelli",
        "club_id": "arsenal",
        "name": "Gabriel Martinelli",
        "short_name": "G. Martinelli",
        "position": "Attacker",
        "jersey_number": 11,
        "nationality": "Brazil",
        "appearances": 33,
        "goals": 9,
        "assists": 6,
        "clean_sheets": 0,
        "minutes_played": 2380,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-gabriel-martinelli-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-gabriel-martinelli-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-gabriel-martinelli-action.jpg",
        "bio": "Explosive left-wing sprinter who stretches high lines vertically and tracks back relentlessly on transition. Deadly when attacking the back post or darting behind full-backs.",
        "date_of_birth": "2001-06-18",
        "height": "178 cm",
        "joined_date": "July 2019",
    },
    {
        "id": "ply_gyokeres",
        "club_id": "arsenal",
        "name": "Viktor Gyökeres",
        "short_name": "V. Gyökeres",
        "position": "Attacker",
        "jersey_number": 14,
        "nationality": "Sweden",
        "appearances": 30,
        "goals": 18,
        "assists": 5,
        "clean_sheets": 0,
        "minutes_played": 2480,
        "yellow_cards": 3,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-viktor-gyokeres-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-viktor-gyokeres-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-viktor-gyokeres-action.jpg",
        "bio": "Prolific No. 14 striker signed from Sporting CP to spearhead Arsenal's attack. Combines ferocious channel running and physical hold-up play with clinical two-footed finishing.",
        "date_of_birth": "1998-06-04",
        "height": "189 cm",
        "joined_date": "July 2025",
    },
    {
        "id": "ply_trossard",
        "club_id": "arsenal",
        "name": "Leandro Trossard",
        "short_name": "L. Trossard",
        "position": "Attacker",
        "jersey_number": 19,
        "nationality": "Belgium",
        "appearances": 32,
        "goals": 9,
        "assists": 5,
        "clean_sheets": 0,
        "minutes_played": 1840,
        "yellow_cards": 2,
        "red_cards": 1,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-leandro-trossard-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-leandro-trossard-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-leandro-trossard-action.jpg",
        "bio": "Clutch two-footed technician who thrives across the left wing and false-nine slots. Arsenal's supreme penalty-box ice-man when matches tighten late in the second half.",
        "date_of_birth": "1994-12-04",
        "height": "172 cm",
        "joined_date": "January 2023",
    },
    {
        "id": "ply_madueke",
        "club_id": "arsenal",
        "name": "Noni Madueke",
        "short_name": "N. Madueke",
        "position": "Attacker",
        "jersey_number": 20,
        "nationality": "England",
        "appearances": 22,
        "goals": 5,
        "assists": 4,
        "clean_sheets": 0,
        "minutes_played": 1310,
        "yellow_cards": 2,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-noni-madueke-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-noni-madueke-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-noni-madueke-action.jpg",
        "bio": "Direct, high-volume 1v1 dribbler capable of operating on both flanks. Gives Arteta explosive isolation speed against tired full-backs and fierce left-footed strikes off the right wing.",
        "date_of_birth": "2002-03-10",
        "height": "182 cm",
        "joined_date": "July 2025",
    },
    {
        "id": "ply_havertz",
        "club_id": "arsenal",
        "name": "Kai Havertz",
        "short_name": "K. Havertz",
        "position": "Attacker",
        "jersey_number": 29,
        "nationality": "Germany",
        "appearances": 31,
        "goals": 13,
        "assists": 5,
        "clean_sheets": 0,
        "minutes_played": 2520,
        "yellow_cards": 4,
        "red_cards": 0,
        "photo_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-kai-havertz-portrait.png",
        "portrait_url": "https://assets.arsenal.com/prod/images/square_1000_1000/arsenalmenssquad2627-kai-havertz-portrait.png",
        "action_url": "https://assets.arsenal.com/prod/images/action/arsenalmenssquad2627-kai-havertz-action.jpg",
        "bio": "Intelligent spatial raumdeuter linking Arsenal's midfield and frontline. Wins crucial long-ball outlets, ghosts into blind-side pockets, and sets the intensity of Arsenal's high press.",
        "date_of_birth": "1999-06-11",
        "height": "193 cm",
        "joined_date": "June 2023",
    },
]


def _player_model_to_dict(p: Player) -> dict:
    return {
        "id": p.id,
        "club_id": p.club_id,
        "name": p.name,
        "short_name": p.short_name,
        "position": p.position,
        "jersey_number": p.jersey_number,
        "nationality": p.nationality,
        "appearances": p.appearances,
        "goals": p.goals,
        "assists": p.assists,
        "clean_sheets": p.clean_sheets,
        "minutes_played": p.minutes_played,
        "yellow_cards": p.yellow_cards,
        "red_cards": p.red_cards,
        "photo_url": p.photo_url,
        "portrait_url": p.portrait_url,
        "action_url": p.action_url,
        "bio": p.bio,
        "date_of_birth": p.date_of_birth,
        "height": p.height,
        "joined_date": p.joined_date,
    }


def format_player_response(p: dict) -> PlayerDetailResponse:
    apps = max(p.get("appearances", 1), 1)
    goals = p.get("goals", 0)
    assists = p.get("assists", 0)
    return PlayerDetailResponse(
        id=p["id"],
        club_id=p["club_id"],
        name=p["name"],
        short_name=p["short_name"],
        position=p["position"],
        jersey_number=p["jersey_number"],
        nationality=p["nationality"],
        appearances=p.get("appearances", 0),
        goals=goals,
        assists=assists,
        clean_sheets=p.get("clean_sheets", 0),
        minutes_played=p.get("minutes_played", 0),
        yellow_cards=p.get("yellow_cards", 0),
        red_cards=p.get("red_cards", 0),
        photo_url=p.get("photo_url"),
        portrait_url=p.get("portrait_url"),
        action_url=p.get("action_url"),
        bio=p.get("bio"),
        date_of_birth=p.get("date_of_birth"),
        height=p.get("height"),
        joined_date=p.get("joined_date"),
        goals_per_game=round(goals / apps, 2),
        assists_per_game=round(assists / apps, 2),
        goal_contributions=goals + assists
    )


def build_comparison_item(p: PlayerResponse) -> PlayerComparisonItem:
    minutes = max(p.minutes_played, 90)
    contributions = max(p.goal_contributions, 1)
    return PlayerComparisonItem(
        player=p,
        goals_per_90=round((p.goals / minutes) * 90, 2),
        assists_per_90=round((p.assists / minutes) * 90, 2),
        minutes_per_contribution=round(minutes / contributions, 1),
        discipline_score=round(10.0 - (p.yellow_cards * 0.5 + p.red_cards * 2.0), 1)
    )


@router.get("", response_model=List[PlayerResponse])
async def list_squad(
    club_id: Optional[str] = Query(None, description="Filter squad by club"),
    position: Optional[str] = Query(None, description="Filter by position (Goalkeeper, Defender, Midfielder, Attacker)"),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve club squad list with full player profiles and statistics (DB-first)."""
    total_in_db = (await db.execute(select(func.count(Player.id)))).scalar() or 0
    if total_in_db > 0:
        stmt = select(Player)
        if club_id:
            stmt = stmt.where(Player.club_id == club_id)
        if position:
            stmt = stmt.where(func.lower(Player.position) == position.lower())
        stmt = stmt.order_by(Player.jersey_number.asc())
        db_players = (await db.execute(stmt)).scalars().all()
        return [format_player_response(_player_model_to_dict(p)) for p in db_players]

    # Cold-start baseline fallback when players table is empty
    players = DEFAULT_PLAYERS
    if club_id:
        players = [p for p in players if p["club_id"] == club_id]
    if position:
        players = [p for p in players if p["position"].lower() == position.lower()]

    return [format_player_response(p) for p in sorted(players, key=lambda item: item["jersey_number"])]


@router.get("/compare", response_model=PlayerComparisonResponse)
async def compare_players(
    player1_id: str = Query(..., description="First player ID"),
    player2_id: str = Query(..., description="Second player ID"),
    db: AsyncSession = Depends(get_db)
):
    """Compare two players head-to-head across key performance metrics (DB-first)."""
    db_p1 = (await db.execute(select(Player).where(Player.id == player1_id))).scalar_one_or_none()
    db_p2 = (await db.execute(select(Player).where(Player.id == player2_id))).scalar_one_or_none()

    p1_dict = _player_model_to_dict(db_p1) if db_p1 else None
    p2_dict = _player_model_to_dict(db_p2) if db_p2 else None

    if not p1_dict or not p2_dict:
        total_in_db = (await db.execute(select(func.count(Player.id)))).scalar() or 0
        if total_in_db == 0:
            if not p1_dict:
                p1_dict = next((p for p in DEFAULT_PLAYERS if p["id"] == player1_id), None)
            if not p2_dict:
                p2_dict = next((p for p in DEFAULT_PLAYERS if p["id"] == player2_id), None)

    if not p1_dict or not p2_dict:
        raise HTTPException(status_code=404, detail="One or both players not found")

    p1_resp = format_player_response(p1_dict)
    p2_resp = format_player_response(p2_dict)

    item1 = build_comparison_item(p1_resp)
    item2 = build_comparison_item(p2_resp)

    if item1.player.goal_contributions > item2.player.goal_contributions:
        leader = item1.player.name
        summary = f"{leader} leads in total direct goal contributions ({item1.player.goal_contributions} vs {item2.player.goal_contributions})."
    elif item2.player.goal_contributions > item1.player.goal_contributions:
        leader = item2.player.name
        summary = f"{leader} leads in total direct goal contributions ({item2.player.goal_contributions} vs {item1.player.goal_contributions})."
    else:
        summary = f"Both players are level with {item1.player.goal_contributions} direct goal contributions."

    return PlayerComparisonResponse(
        player1=item1,
        player2=item2,
        comparison_summary=summary
    )


@router.get("/{player_id}", response_model=PlayerDetailResponse)
async def get_player(
    player_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single player profile details and scouting dossier (DB-first)."""
    db_p = (await db.execute(select(Player).where(Player.id == player_id))).scalar_one_or_none()
    if db_p:
        return format_player_response(_player_model_to_dict(db_p))

    total_in_db = (await db.execute(select(func.count(Player.id)))).scalar() or 0
    if total_in_db == 0:
        p_dict = next((p for p in DEFAULT_PLAYERS if p["id"] == player_id), None)
        if p_dict:
            return format_player_response(p_dict)

    raise HTTPException(status_code=404, detail="Player not found")
