import React, { useState } from 'react';
import '../allCss/teams.css';
import ALBERT_SAMBI from '../assets/playerImages/ALBERT_SAMBI.png';
import BEN_WHITE from '../assets/playerImages/BEN_WHITE.png';
import BUKAYO_SAKA from '../assets/playerImages/BUKAYO_SAKA.png';
import DECLAN_RICE from '../assets/playerImages/DECLAN_RICE.png';
import FABIO_VIEIRA from '../assets/playerImages/FABIO_VIEIRA.png';
import GABRIEL from '../assets/playerImages/GABRIEL.png';
import JESUS from '../assets/playerImages/JESUS.png';
import MARTINI from '../assets/playerImages/NETO.png';
import NETO from '../assets/playerImages/MARTINI.png';
import JAKUB from '../assets/playerImages/JAKUB.png';
import JORGINHO from '../assets/playerImages/JORGINHO.png';
import JURRIEN from '../assets/playerImages/JURRIEN.png';
import KAI from '../assets/playerImages/KAI.png';
import KARL from '../assets/playerImages/KARL.png';
import TIERNEY from '../assets/playerImages/TIERNEY.png';
import TROSS from '../assets/playerImages/TROSS.png';
import MARQUINHOS from '../assets/playerImages/MARQUINHOS.png';
import MERINO from '../assets/playerImages/MERINO.png';
import NUNO from '../assets/playerImages/NUNO.png';
import ODEGARD from '../assets/playerImages/ODEGARD.png';
import OLEKSANDR from '../assets/playerImages/OLEKSANDR.png';

import STERLING from '../assets/playerImages/STERLING.png';
import NELSON from '../assets/playerImages/NELSON.png';
import REYA from '../assets/playerImages/REYA.png';
import CALAFIORI from '../assets/playerImages/CALAFIORI.png';
import TOMIYASU from '../assets/playerImages/TOMIYASU.png';
import PARTEY from '../assets/playerImages/PARTEY.png';
import SALIBA from '../assets/playerImages/SALIBA.png';
import KAMRUDDIN from '../assets/playerImages/KAMRUDDIN.jpg';
import SADIK from '../assets/playerImages/SADIK.jpg';
import RAKIBUL from '../assets/playerImages/RAKIBUL.jpg';
import ZINSBERGER from '../assets/playerImages/women/ZINSBERGER.png';
import VAN from '../assets/playerImages/women/VAN.png';
import NAOMI from '../assets/playerImages/women/NAOMI.png';
import EMILY from '../assets/playerImages/women/EMILY.png';
import LOTTE from '../assets/playerImages/women/LOTTE.png';
import WILLIAMSON from '../assets/playerImages/women/WILLIAMSON.png';
import CODINA from '../assets/playerImages/women/CODINA.png';
import CATLEY from '../assets/playerImages/women/CATLEY.png';
import MCCABE from '../assets/playerImages/women/MCCABE.png';
import LAURA from '../assets/playerImages/women/LAURA.png';
import ILESTEDT from '../assets/playerImages/women/ILESTEDT.png';


import LITTLE from '../assets/playerImages/women/LITTLE.png';
import MAANUM from '../assets/playerImages/women/MAANUM.png';
import WALTI from '../assets/playerImages/women/WALTI.png';
import PELOVA from '../assets/playerImages/women/PELOVA.png';
import KUHL from '../assets/playerImages/women/KUHL.png';
import CROSS from '../assets/playerImages/women/CROSS.png';
import MEAD from '../assets/playerImages/women/MEAD.png';

import HURTIG from '../assets/playerImages/women/HURTIG.png';
import FOORD from '../assets/playerImages/women/FOORD.png';
import RUSSO from '../assets/playerImages/women/RUSSO.png';
import BLACKSTENIUS from '../assets/playerImages/women/BLACKSTENIUS.png';

import GODFREY from '../assets/playerImages/women/GODFREY.png';
import GOLDIE from '../assets/playerImages/women/GOLDIE.png';


function PlayerInfoPage() {
  const menPlayers = [
    {
      id: 1,
      name: "NORBERTO NETO",
      position: "Goalkeeper",
      number: 32,
      nationality: "Brazil",
      image: NETO
    },
    {
      id: 2,
      name: "DAVID RAYA",
      position: "Goalkeeper",
      number: 2,
      nationality: "Spain",
      image: REYA    },
    {
      id: 3,
      name: "KARL HEIN",
      position: "Goalkeeper",
      number: 34,
      nationality: "Estonia",
      image: KARL    },
    {
      id: 4,
      name: "WILLIAM SALIBA",
      position: "Defender",
      number: 14,
      nationality: "France",
      image: SALIBA,
      onLoan: true

          },
    {
      id: 5,
      name: "BEN WHITE",
      position: "Defender",
      number: 4,
      nationality: "England",
      image: BEN_WHITE
      
    },
    {
      id: 6,
      name: "GABRIEL",
      position: "Defender",
      number: 6,
      nationality: "Brazil",
      onLoan: false,
      image: GABRIEL
    },
    {
        id: 7,
        name: "JURRIEN TIMBER",
        position: "Defender",
        number: 12,
        nationality: "Netherlands",
        onLoan: false,
        image:JURRIEN


  
      },
      {
        id: 8,
        name: "JAKUB KIWIOR",
        position: "Defender",
        number: 15,
        nationality: "Poland",
        onLoan: false,
        image:JAKUB
      },{
        id:33,
        name: "RICCARDO CALAFIORI",
        position: "Defender",
        number: 33,
        nationality: "ITALY",
        onLoan: false,
        image:CALAFIORI
      },{
        id: 10,
        name: "TAKEHIRO TOMIYASU",
        position: "Defender",
        number: 18,
        nationality: "Japan",
        onLoan: false,
        image:TOMIYASU
      },
      {
        id: 11,
        name: "OLEKSANDR ZINCHENKO",
        position: "Defender",
        number: 35,
        nationality: "Ukraine",
        onLoan: false,
        image:OLEKSANDR
      },
      {
        id: 12,
        name: "THOMAS",
        position: "Midfielder",
        number: 5,
        nationality: "Ghana",
        image: PARTEY,
        onLoan: false
      },
      {
        id: 13,
        name: "MARTIN ODEGARD",
        position: "Midfielder",
        number: 8,
        nationality: "Norway",
        image: ODEGARD,
        onLoan: false
      },
      {
        id: 14,
        name: "MIKEL MERINO",
        position: "Midfielder",
        number: 23,
        nationality: "Spain",
        onLoan: false,
        image:MERINO,
      },
      {
        id: 15,
        name: "JORGINHO",
        position: "Midfielder",
        number: 20,
        nationality: "Italy",
        image:JORGINHO,
                onLoan: false
      },
      {
        id: 16,
        name: "FABIO VEIERA",
        position: "Midfielder",
        number: 21,
        nationality: "Portugal",
        onLoan: false,
        image: FABIO_VIEIRA
      },
      
      
      {
        id: 19,
        name: "DECLAN RICE",
        position: "Midfielder",
        number: 5,
        nationality: "England",
        onLoan: false,
        image: DECLAN_RICE
      },
      {
        id: 20,
        name: "BUKAYO SAKA",
        position: "Forward",
        number: 7,
        nationality: "England",
        onLoan: false,
        image: BUKAYO_SAKA
      },
      {
        id: 21,
        name: "GABRIEL JESUS",
        position: "Forward",
        number: 9,
        nationality: "Brazil",
        onLoan: false,
        image: JESUS
      },
      {
        id: 22,
        name: "GABRIEL MARTINELLI",
        position: "Forward",
        number: 11,
        nationality: "Brazil",
        onLoan: false,
        image: MARTINI,
      },
      {
        id: 23,
        name: "LEANDRO TROSSARD",
        position: "Forward",
        number: 14,
        nationality: "Belgium",
        onLoan: false,
        image:TROSS
      },
      
      {
        id: 25,
        name: "REISS NELSON",
        position: "Forward",
        number: 24,
        nationality: "England",
        onLoan: true,
        image: NELSON
      },
      {
        id: 26,
        name: "RAHEEM STERLING",
        position:"Forward",
        number: 30,
        nationality: "England",
        onLoan: true,
        image: STERLING
      },
      {
        id: 27,
        name: "KIERAN TIERNEY",
        
        number: 3,
        nationality: "Scotland",
        onLoan: true,
        image: TIERNEY
      },
      {
        id: 28,
        name: "NUNO TAVARES",
        
        number: 20,
        nationality: "Portugal",
        onLoan: true,
        image: NUNO
      },
      {
        id: 29,
        name: "ALBERT LOKONGA",
        
        number: 24,
        nationality: "Belgium",
        onLoan: true,
        image:ALBERT_SAMBI
      },
      {
        id: 30,
        name: "OG KAMRUDDIN",
        
        number: 69,
        nationality: "Cumilla",
        onLoan: true,
        image: KAMRUDDIN
      }
      ,
      
      {
        id: 32,
        name: "FABIO VIEIRA",
        
        number: 21,
        nationality: "Portugal",
        onLoan: true,
        image:  FABIO_VIEIRA
      }, 
      {
        id: 33,
        name: "CHOCO SADIK ",
        
        number: 21,
        nationality: "Pahari",
        onLoan: true,
        image: SADIK,
      }, 
      {
        id: 34,
        name: "RAKIBUL",
        
        number: 4,
        nationality: "Dhaka",
        onLoan: true,
        image: RAKIBUL
      }, 
    //... more players
  ];

  const womenPlayers = [
    {
      id: 1,
      name: "MANUELA ZINSBERGER",
      position: "Goalkeeper",
      number: 1,
      nationality: "Austria",
      image: ZINSBERGER,
    },
    {
      id: 2,
      name: "VAN SOMSELAAR",
      position: "Goalkeeper",
      number: 14,
      nationality: "Netherlands",
      image: VAN,
    },
    {
      id: 3,
      name: "NAOMI WILLIAMS",
      position: "Goalkeeper",
      number: 40,
      nationality: "England",
      image: NAOMI,
    },
    {
      id: 45,
      name: "EMILY FOX",
      position: "Defender",
      number: 2,
      nationality: "USA",
      image: EMILY,
    },
    {
      id: 4,
      name: "LOTTE WUBBEN",
      position: "Defender",
      number: 2,
      nationality: "ENGLAND",
      image: LOTTE,
    },
    {
      id: 5,
      name: "LEAH WILLIAMSON",
      position: "Defender",
      number: 2,
      nationality: "England",
      image: WILLIAMSON,
    },
    {
      id: 50,
      name: "LAIA CODINA",
      position: "Defender",
      number: 5,
      nationality: "Spain",
      image: CODINA,
    },
    {
      id: 6,
      name: "STEPH CATLEY",
      position: "Defender",
      number: 7,
      nationality: "USA",
      image: CATLEY,
    },
    {
      id: 7,
      name: "KATIE MCCABE",
      position: "Defender",
      number: 2,
      nationality: "Republic of Ireland",
      image: MCCABE,
    },
    {
      id: 8,
      name: "LAURA WIENROITHER",
      position: "Defender",
      number: 26,
      nationality: "Austria",
      image: LAURA,
    },
    {
      id: 9,
      name: "AMANDA ILESTEDT",
      position: "Defender",
      number: 28,
      nationality: "Sweden",
      image: ILESTEDT,
    },
    {
      id: 10,
      name: "TEYAH GOLDIE",
      position: "Defender",
      number: 2,
      nationality: "England",
      onLoan: true,
      image: GOLDIE,
    },
    {
      id: 11,
      name: "KIM LITTLE",
      position: "Midfielder",
      number: 2,
      nationality: "Scotland",
      image: LITTLE,
    },
    {
      id: 12,
      name: "FRIDA MAANUM",
      position: "Midfielder",
      number: 12,
      nationality: "England",
      image: MAANUM,
    },
    {
      id: 13,
      name: "LIA WALTI",
      position: "Midfielder",
      number: 13,
      nationality: "England",
      image: WALTI,
    },
    {
      id: 14,
      name: "VICTORIA PELOVA",
      position: "Midfielder",
      number: 21,
      nationality: "Netherlands",
      image: PELOVA,
    },
    {
      id: 15,
      name: "KATHRINE KUHL",
      position: "Midfielder",
      number: 22,
      nationality: "Denmark",
      image: KUHL,
    },
    {
      id: 16,
      name: "COONEY-CROSS",
      position: "Midfielder",
      number: 32,
      nationality: "Australia",
      image: CROSS,
    },
    {
      id: 17,
      name: "BETH MEAD",
      position: "Forward",
      number: 9,
      nationality: "England",
      image: MEAD,
    },
    {
      id: 18,
      name: "STINA BLACKSTENIUS",
      position: "Forward",
      number: 11,
      nationality: "Sweden",
      image: BLACKSTENIUS,
    },
    {
      id: 19,
      name: "LINA HURTIG",
      position: "Forward",
      number: 17,
      nationality: "Sweden",
      image: HURTIG,
    },
    {
      id: 20,
      name: "CAITLIN FOORD",
      position: "Forward",
      number: 19,
      nationality: "Australia",
      image: FOORD,
    },
    {
      id: 21,
      name: "ALESSIA RUSSO",
      position: "Forward",
      number: 21,
      nationality: "England",
      image: RUSSO,
    },
    {
      id: 22,
      name: "FREYA GODFREY",
      position: "Forward",
      number: 56,
      nationality: "Canada",
      image: GODFREY,
    },
    
  ];

  const [selectedTeam, setSelectedTeam] = useState('men');
  const players = selectedTeam === 'men' ? menPlayers : womenPlayers;

  const goalkeepers = players.filter(player => player.position === "Goalkeeper");
  const defenders = players.filter(player => player.position === "Defender");
  const midfielders = players.filter(player => player.position === "Midfielder");
  const forwards = players.filter(player => player.position === "Forward");
  const onLoan = players.filter(player => player.onLoan === true);
/*  main code */
  return (
    <div className="white-section">
      <h1 className="centered-title">Players</h1>
      
      <label htmlFor="teamSelect">Select Team: </label>
      <select
        id="teamSelect"
        value={selectedTeam}
        onChange={(e) => setSelectedTeam(e.target.value)}
        className="styled-select"
      >
        <option value="men">Men</option>
        <option value="women">Women</option>
      </select>
  
      <h2 className="centered-title">Goalkeepers</h2>
      <ul className="player-list">
        {goalkeepers.map(player => (
          <li key={player.id} className="player-item">
            <img src={player.image} alt={player.name} width={50} height={50} />
            <div>
              <h3>{player.name}</h3>
              <p><strong>{player.number}</strong></p>
              <p>{player.nationality}</p>
            </div>
          </li>
        ))}
      </ul>
      
      <h2 className="centered-title">Defenders</h2>
      <ul className="player-list">
        {defenders.map(player => (
          <li key={player.id} className="player-item">
            <img src={player.image} alt={player.name} width={50} height={50} />
            <div>
              <h3>{player.name}</h3>
              <p><strong>{player.number}</strong></p>
              <p>{player.nationality}</p>
            </div>
          </li>
        ))}
      </ul>
  
      <h2 className="centered-title">Midfielders</h2>
      <ul className="player-list">
        {midfielders.map(player => (
          <li key={player.id} className="player-item">
            <img src={player.image} alt={player.name} width={50} height={50} />
            <div>
              <h3>{player.name}</h3>
              <p><strong>{player.number}</strong></p>
              <p>{player.nationality}</p>
            </div>
          </li>
        ))}
      </ul>
  
      <h2 className="centered-title">Forwards</h2>
      <ul className="player-list">
        {forwards.map(player => (
          <li key={player.id} className="player-item">
            <img src={player.image} alt={player.name} width={50} height={50} />
            <div>
              <h3>{player.name}</h3>
              <p><strong>{player.number}</strong></p>
              <p>{player.nationality}</p>
            </div>
          </li>
        ))}
      </ul>
  
      <h2 className="centered-title">On Loan</h2>
      <ul className="player-list">
        {onLoan.map(player => (
          <li key={player.id} className="player-item">
            <img src={player.image} alt={player.name} width={50} height={50} />
            <div>
              <h3>{player.name}</h3>
              <p><strong>{player.number}</strong></p>
              <p>{player.nationality}</p>
            </div>
          </li>
        ))}
      </ul>
      <footer>
        <p>&copy; 2024 Arsenal FC Fan Page</p>
      </footer>
    </div>
  );
}

export default PlayerInfoPage;
