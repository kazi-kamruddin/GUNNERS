import arsenalLogo from '../assets/ClubLogos/arsenal.png';
import chelseaLogo from '../assets/ClubLogos/chelsea.png';
import manCityLogo from '../assets/ClubLogos/man city.png';
import manUnitedLogo from '../assets/ClubLogos/man united.png';
import realMadridLogo from '../assets/ClubLogos/real madrid.png';
import barcaLogo from '../assets/ClubLogos/barcelona.png';
import milanLogo from '../assets/ClubLogos/ac milan.png';
import westHamLogo from '../assets/ClubLogos/west ham.png';
import liverpoolLogo from '../assets/ClubLogos/liverpool.png';

const logos = {
    'Arsenal': arsenalLogo,
    'arsenal': arsenalLogo,
    'ARSENAL': arsenalLogo,
    'Liverpool': liverpoolLogo,
    'liverpool': liverpoolLogo,
    'LIVERPOOL': liverpoolLogo,
    'Manchester City': manCityLogo,
    'manchester city': manCityLogo,
    'MAN CITY': manCityLogo,
    'Man City': manCityLogo,
    'man city': manCityLogo,
    'MANCHESTER CITY': manCityLogo,
    'Manchester United': manUnitedLogo,
    'manchester united': manUnitedLogo,
    'MANCHESTER UNITED': manUnitedLogo,
    'Man United': manUnitedLogo,
    'man united': manUnitedLogo,
    'MAN UNITED': manUnitedLogo,
    'AC Milan': milanLogo,
    'ac milan': milanLogo,
    'AC MILAN': milanLogo,
    'Barcelona': barcaLogo,
    'barcelona': barcaLogo,
    'BARCELONA': barcaLogo,
    'Real Madrid': realMadridLogo,
    'real madrid': realMadridLogo,
    'REAL MADRID': realMadridLogo,
    'West Ham': westHamLogo,
    'west ham': westHamLogo,
    'WEST HAM': westHamLogo,
    'Chelsea': chelseaLogo,
    'chelsea': chelseaLogo,
    'CHELSEA': chelseaLogo,
};

export const getLogo = (clubName) => {
    return logos[clubName] || null; 
};
