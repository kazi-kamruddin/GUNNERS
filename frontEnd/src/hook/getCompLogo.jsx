import uclLogo from '../assets/TournamentLogos/uclLogo.png';
import carabaoLogo from '../assets/TournamentLogos/carabaoLogo.png';
import europaLogo from '../assets/TournamentLogos/europaLogo.png';
import plLogo from '../assets/TournamentLogos/plLogo.png';
import faCupLogo from '../assets/TournamentLogos/faCupLogo.png';

const compLogos = {
    'uefa champions league': uclLogo,
    'UEFA CHAMPIONS LEAGUE': uclLogo,
    'Uefa Champions League': uclLogo,
    'UEFA Champions League' : uclLogo,
    'UCL': uclLogo,
    'ucl': uclLogo,
    'fa cup': faCupLogo,
    'FA CUP': faCupLogo,
    'Fa Cup': faCupLogo,
    'FA Cup': faCupLogo,
    'premiere league': plLogo,
    'PREMIERE LEAGUE': plLogo,
    'Premiere League': plLogo,
    'PL': plLogo,
    'pl': plLogo,
    'carabao cup': carabaoLogo,
    'CARABAO CUP': carabaoLogo,
    'Carabao Cup': carabaoLogo,
    'europa league': europaLogo,
    'EUROPA LEAGUE': europaLogo,
    'Europa League': europaLogo,
};

export const getCompLogo = (compName) => {
    return compLogos[compName] || null; 
};
