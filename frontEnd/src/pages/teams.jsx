import React, { useState } from 'react';
import '../allCss/teams.css';

function PlayerInfoPage() {
  const menPlayers = [
    {
      id: 1,
      name: "AARON RAMSDALE",
      position: "Goalkeeper",
      number: 1,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Ramsdale_1510x850_0.jpg?auto=webp&itok=w6EQqPOI/200x200"
    },
    {
      id: 2,
      name: "DAVID RAYA",
      position: "Goalkeeper",
      number: 2,
      nationality: "Spain",
      image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Raya%20website%20profile%20image.png?auto=webp&itok=qs9f8267/200x200"
    },
    {
      id: 3,
      name: "KARL HEIN",
      position: "Goalkeeper",
      number: 34,
      nationality: "Estonia",
      image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Hein_1510x850_0.jpg?auto=webp&itok=Olojclw9/100x100"
    },
    {
      id: 4,
      name: "WILLIAM SALIBA",
      position: "Defender",
      number: 14,
      nationality: "France",

      image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/MicrosoftTeams-image%20%2831%29_0.png?auto=webp&itok=zY0rjgVn/100x100"
    },
    {
      id: 5,
      name: "BEN WHITE",
      position: "Defender",
      number: 4,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_White_1510x850_0.jpg?auto=webp&itok=iUyWTT7l/100x100"
    },
    {
      id: 6,
      name: "GABRIEL",
      position: "Defender",
      number: 6,
      nationality: "Brazil",
      image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Gabriel_1510x850_0.jpg?auto=webp&itok=_bv57iX5/100x100",
      onLoan: false
    },
    {
        id: 7,
        name: "JURRIEN TIMBER",
        position: "Defender",
        number: 12,
        nationality: "Netherlands",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/MicrosoftTeams-image%20%2827%29_0.png?auto=webp&itok=9GPY-bZ8/100x100",
        onLoan: false
      },
      {
        id: 8,
        name: "JAKUB KIWIOR",
        position: "Defender",
        number: 15,
        nationality: "Poland",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Kiwior_1510x850_0.jpg?auto=webp&itok=iGge9AQ8/100x100",
        onLoan: false
      },{
        id: 9,
        name: "CEDRIC",
        position: "Defender",
        number: 17,
        nationality: "Portugal",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/MicrosoftTeams-image%20%2828%29_1.png?auto=webp&itok=tiiU8DLt/100x100",
        onLoan: false
      },{
        id: 10,
        name: "TAKEHIRO TOMIYASU",
        position: "Defender",
        number: 18,
        nationality: "Japan",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/MicrosoftTeams-image%20%2832%29_0.png?auto=webp&itok=i6UFe3mR/100x100",
        onLoan: false
      },
      {
        id: 11,
        name: "OLEKSANDR ZINCHENKO",
        position: "Defender",
        number: 35,
        nationality: "Ukraine",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Zinchenko_1510x850_0.jpg?auto=webp&itok=xxf95c-H/100x100",
        onLoan: false
      },
      {
        id: 12,
        name: "THOMAS",
        position: "Midfielder",
        number: 5,
        nationality: "Ghana",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Partey_1510x850_0.jpg?auto=webp&itok=l8_scPxh",
        onLoan: false
      },
      {
        id: 13,
        name: "MARTIN ODEGARD",
        position: "Midfielder",
        number: 8,
        nationality: "Norway",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Odegaard_1510x850_0.jpg?auto=webp&itok=YQO9ByvO",
        onLoan: false
      },
      {
        id: 14,
        name: "EMILE SMITH ROWE",
        position: "Midfielder",
        number: 10,
        nationality: "England",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_SmithRowe_1510x850_0.jpg?auto=webp&itok=Inf1oGOt",
        onLoan: false
      },
      {
        id: 15,
        name: "JORGINHO",
        position: "Midfielder",
        number: 20,
        nationality: "Italy",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Jorginho_1510x850_0.jpg?auto=webp&itok=Nf9aKZ1_",
        onLoan: false
      },
      {
        id: 16,
        name: "FABIO VEIERA",
        position: "Midfielder",
        number: 21,
        nationality: "Portugal",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Vieira_1510x850_0.jpg?auto=webp&itok=IU_d4QjL",
        onLoan: false
      },
      {
        id: 17,
        name: "MOHAMED ELNENY",
        position: "Midfielder",
        number: 25,
        nationality: "Egypt",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Elneny_1510x850_0.jpg?auto=webp&itok=vB0SjbIG",
        onLoan: false
      },
      {
        id: 18,
        name: "KAI HAVERTZ",
        position: "Midfielder",
        number: 29,
        nationality: "Germany",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Havertz_1510x850_0.jpg?auto=webp&itok=iTguU7_8",
        onLoan: false
      },
      {
        id: 19,
        name: "DECLAN RICE",
        position: "Midfielder",
        number: 5,
        nationality: "England",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/MicrosoftTeams-image%20%2826%29.png?auto=webp&itok=K8hmFn_d",
        onLoan: false
      },
      {
        id: 20,
        name: "BUKAYO SAKA",
        position: "Forward",
        number: 7,
        nationality: "England",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Saka_1510x850_0.jpg?auto=webp&itok=yZpptHcr",
        onLoan: false
      },
      {
        id: 21,
        name: "GABRIEL JESUS",
        position: "Forward",
        number: 9,
        nationality: "Brazil",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Jesus_1510x850_0.jpg?auto=webp&itok=ATg3CJe1",
        onLoan: false
      },
      {
        id: 22,
        name: "GABRIEL MARTINELLI",
        position: "Forward",
        number: 11,
        nationality: "Brazil",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Martinelli_1510x850.jpg?auto=webp&itok=gAO5wDqg",
        onLoan: false
      },
      {
        id: 23,
        name: "EDDIE NKETIAH",
        position: "Forward",
        number: 14,
        nationality: "England",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Nketiah_1510x850_0.jpg?auto=webp&itok=k3BjsLa_",
        onLoan: false
      },
      {
        id: 24,
        name: "LEANDRO TROSSARD",
        position: "Forward",
        number: 19,
        nationality: "Belgium",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Trossard_1510x850_0.jpg?auto=webp&itok=VEq3JA_C",
        onLoan: false
      },
      {
        id: 25,
        name: "REISS NELSON",
        position: "Forward",
        number: 24,
        nationality: "England",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/Headshot_Nelson_1510x850_0.jpg?auto=webp&itok=0UCRfAz2",
        onLoan: false
      },
      {
        id: 26,
        name: "ARTHUR OKONKWO",
        
        number: 33,
        nationality: "England",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/okonkwo_.com_headshot.jpg?auto=webp&itok=gs0QD3SN",
        onLoan: true
      },
      {
        id: 27,
        name: "KIERAN TIERNEY",
        
        number: 3,
        nationality: "Scotland",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/MicrosoftTeams-image%20%2830%29_0.png?auto=webp&itok=--9BLn7K",
        onLoan: true
      },
      {
        id: 28,
        name: "NUNO TAVARES",
        
        number: 20,
        nationality: "Portugal",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/tavares_.com_headshot.jpg?auto=webp&itok=eNwLdzDz",
        onLoan: true
      },
      {
        id: 29,
        name: "ALBERT LOKONGA",
        
        number: 24,
        nationality: "Belgium",
        image: "https://www.arsenal.com/sites/default/files/styles/large_16x9/public/images/lokonga_.com_headshot.jpg?auto=webp&itok=LDHhQUzS",
        onLoan: true
      },
      {
        id: 30,
        name: "OG KAMRUDDIN",
        
        number: 69,
        nationality: "Cumilla",
        image: "https://scontent.fdac14-1.fna.fbcdn.net/v/t39.30808-1/395347123_856999322675140_1235572987313974752_n.jpg?stp=dst-jpg_s200x200&_nc_cat=105&ccb=1-7&_nc_sid=5f2048&_nc_eui2=AeG7L-HbTFBx0dIlS2dDG321LxmMZEFcq9EvGYxkQVyr0dnBC8bYqoGlCFReoa98HWU6W9edFffFH1jgxAdl-t3b&_nc_ohc=ZXYlMkVOgiEQ7kNvgH_vBsF&_nc_ht=scontent.fdac14-1.fna&oh=00_AYApfbdlcWK1zc788fBIEHY3obWMyWVmDaEAtLBRXT-6zw&oe=667CD66C",
        onLoan: true
      }
    //... more players
  ];

  const womenPlayers = [
    {
      id: 1,
      name: "MANUELA ZINSBERGER",
      position: "Goalkeeper",
      number: 1,
      nationality: "Austria",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Zinsberger_2.jpg?auto=webp&itok=Q9nadxHN"
    },
    {
      id: 2,
      name: "SABRINA DANGELO",
      position: "Goalkeeper",
      number: 14,
      nationality: "Canada",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/D%27Angelo.jpg?auto=webp&itok=RohPVTFS"
    },

    {
      id: 3,
      name: "KAYLAN MARKESE",
      position: "Goalkeeper",
      number: 18,
      nationality: "USA",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Kaylan%20Marckese.png?auto=webp&itok=Xqs2V70E"
    },
    {
      id: 3,
      name: "NAOMI WILLIAMS",
      position: "Goalkeeper",
      number: 18,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Naomi%20Williams.jpg?auto=webp&itok=TWzKDhLR"
    },
    {
      id: 3,
      name: "EMILY FOX",
      position: "Defender",
      number: 2,
      nationality: "USA",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Emily%20Fox%20headshot.jpg?auto=webp&itok=XE7XHWY3"
    },
    {
      id: 4,
      name: "LOTTE WUBBEN",
      position: "Defender",
      number: 2,
      nationality: "ENGLAND",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Wubben-Moy_0.jpg?auto=webp&itok=xvrlIHTW"
    },
    {
      id: 5,
      name: "LEAH WILLIAMSON",
      position: "Defender",
      number: 2,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Williamson_11.jpg?auto=webp&itok=2ZaHJHRh"
    },
    {
      id: 6,
      name: "STEPH CATLEY",
      position: "Defender",
      number: 7,
      nationality: "USA",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Catley_2.jpg?auto=webp&itok=C7vXtz8p"
    },
    {
      id: 7,
      name: "KATIE MCCABE",
      position: "Defender",
      number: 2,
      nationality: "Republic of Ireland",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/.jpg?auto=webp&itok=a3J4AKNK"
    },
    {
      id: 8,
      name: "LAURA WIENROITHER",
      position: "Defender",
      number: 26,
      nationality: "Austria",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Wienrother.jpg?auto=webp&itok=H3_E6Edk"
    },
    {
      id: 9,
      name: "LAIA CODINA",
      position: "Defender",
      number: 2,
      nationality: "Spain",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Codina.jpg?auto=webp&itok=KoUvWT8L"
    },
    
    {
      id: 10,
      name: "TEYAH GOLDIE",
      position: "Defender",
      number: 2,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Goldie_0.jpg?auto=webp&itok=4SueKtl5"
    },
    {
      id: 11,
      name: "KIM LITTLE",
      position: "Midfielder",
      number: 2,
      nationality: "Scotland",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Kim-Little.jpg?auto=webp&itok=G25pwWNi"
    },
    {
      id: 12,
      name: "FRIDA MAANUM",
      position: "Norway",
      number: 12,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Frida-Maanum.jpg?auto=webp&itok=SWcCT5uh"
    },
    {
      id: 13,
      name: "LIA WALTI",
      position: "Midfielder",
      number: 13,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Lia-Walti.jpg?auto=webp&itok=vU0-drT8"
    },
    {
      id: 14,
      name: "VICTORIA PELOVA",
      position: "Midfielder",
      number: 21,
      nationality: "Netherlands",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Victoria-Pelova.jpg?auto=webp&itok=HRYBaZIh"
    },
    {
      id: 15,
      name: "KATHRINE KUHL",
      position: "Midfielder",
      number: 22,
      nationality: "Denmark",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Kathrine-Kuhl.jpg?auto=webp&itok=ZWpvrl-O"
    },
    {
      id: 16,
      name: "COONEY-CROSS",
      position: "Midfielder",
      number: 32,
      nationality: "Australia",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Kyra.png?auto=webp&itok=FZ7DtBml"
    },
    {
      id: 17,
      name: "BETH MEAD",
      position: "Forwards",
      number: 9,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Vivianne-Miedema.jpg?auto=webp&itok=wOXDgdzm"
    },
    {
      id: 18,
      name: "VIVIEN MIEDIAM",
      position: "Forwards",
      number: 11,
      nationality: "Netherlands",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Lina-Hurtig.jpg?auto=webp&itok=W63lO26I"
    },
    {
      id: 19,
      name: "LINA HURTIG",
      position: "Forwards",
      number: 17,
      nationality: "Sweden",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Lina-Hurtig.jpg?auto=webp&itok=W63lO26I"
    },
    {
      id: 20,
      name: "CAITLIN FORD",
      position: "Forwards",
      number: 19,
      nationality: "Australia",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Caitlin-Foord.jpg?auto=webp&itok=mKmUVCik"
    },
    {
      id: 21,
      name: "ALESSIA RUSSO",
      position: "Forwards",
      number: 21,
      nationality: "England",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Alessia_Russo.jpg?auto=webp&itok=QaGz7Zrv"
    },
    {
      id: 22,
      name: "CLOE LACASSE",
      position: "Forwards",
      number: 24,
      nationality: "Canada",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Cloe-Lacasse.jpg?auto=webp&itok=gCXYPwPB"
    },
    {
      id: 23,
      name: "STINA BLACKSTENIUS",
      position: "Forwards",
      number: 25,
      nationality: "Sweden",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Stina-Blackstenius.jpg?auto=webp&itok=I3Sb5mc0"
    },
    {
      id: 24,
      name: "GIO QUEIROZ",
      position: "Forwards",
      number: 20,
      nationality: "Brazil",
      image: "https://www.arsenal.com/sites/default/files/styles/player_card_large/public/images/Gio-Queiroz.jpg?auto=webp&itok=KHIsbSUT",
      onLoan: true
    },
    
    


    
  ];

  const [selectedTeam, setSelectedTeam] = useState('men');
  const players = selectedTeam === 'men' ? menPlayers : womenPlayers;

  const goalkeepers = players.filter(player => player.position === "Goalkeeper");
  const defenders = players.filter(player => player.position === "Defender");
  const midfielders = players.filter(player => player.position === "Midfielder");
  const forwards = players.filter(player => player.position === "Forward");
  const onLoan = players.filter(player => player.onLoan === true);

  return (
    <div>
      <h1>Players</h1>
      
      <label htmlFor="teamSelect">Select Team: </label>
      <select
        id="teamSelect"
        value={selectedTeam}
        onChange={(e) => setSelectedTeam(e.target.value)}
      >
        <option value="men">Men</option>
        <option value="women">Women</option>
      </select>
  
      <h2>Goalkeepers</h2>
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
  
      <h2>Defenders</h2>
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
  
      <h2>Midfielders</h2>
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
  
      <h2>Forwards</h2>
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
  
      <h2>On Loan</h2>
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
