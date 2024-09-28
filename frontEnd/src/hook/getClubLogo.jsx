import arsenalLogo from '../assets/ClubLogos/arsenal.png';
import chelseaLogo from '../assets/ClubLogos/chelsea.png';
import manCityLogo from '../assets/ClubLogos/man city.png';
import manUnitedLogo from '../assets/ClubLogos/man united.png';
import realMadridLogo from '../assets/ClubLogos/real madrid.png';
import barcaLogo from '../assets/ClubLogos/barcelona.png';
import milanLogo from '../assets/ClubLogos/ac milan.png';
import westHamLogo from '../assets/ClubLogos/west ham.png';
import liverpoolLogo from '../assets/ClubLogos/liverpool.png';
import interMilan from '../assets/ClubLogos/inter milan.png';
import roma from '../assets/ClubLogos/roma.png';
import bayernMunich from '../assets/ClubLogos/bayern munich.png';
import dortmund from '../assets/ClubLogos/borussia dortmund.png';
import leverkusen from '../assets/ClubLogos/bayer leverkusen.png';
import tottenham from '../assets/ClubLogos/tottenham.png';
import psg from '../assets/ClubLogos/psg.png';
import celtic from '../assets/ClubLogos/celtic.png';
import atleticoMadrid from '../assets/ClubLogos/atletico madrid.png';
import benfica from '../assets/ClubLogos/benfica.png';
import brighton from '../assets/ClubLogos/brighton.png';
import newcastle from '../assets/ClubLogos/newcastle.png';
import astonVilla from '../assets/ClubLogos/aston villa.png';
import wolves from '../assets/ClubLogos/wolves.png';
import juventus from '../assets/ClubLogos/juventus.png';
import leicester from '../assets/ClubLogos/leicester.png';

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
    'Leicester City': leicester,
    'leicester city': leicester,
    'LEICESTER CITY': leicester,
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
    'Inter Milan': interMilan,
    'inter milan': interMilan,
    'INTER MILAN': interMilan,
    'Roma': roma,
    'roma': roma,
    'ROMA': roma,
    'Bayern Munich': bayernMunich,
    'bayern munich': bayernMunich,
    'BAYERN MUNICH': bayernMunich,
    'Bayern Munchen': bayernMunich,
    'bayern munchen': bayernMunich,
    'BAYERN MUNCHEN': bayernMunich,
    'Borussia Dortmund': dortmund,
    'borussia dortmund': dortmund,
    'BORUSSIA DORTMUND': dortmund,
    'Bayer Leverkusen': leverkusen,
    'bayer leverkusen': leverkusen,
    'BAYER LEVERKUSEN': leverkusen,
    'Tottenham': tottenham,
    'tottenham': tottenham,
    'TOTTENHAM': tottenham,
    'Paris Saint Germain': psg,
    'paris saint germain': psg,
    'PARIS SAINT GERMAIN': psg,
    'PSG': psg,
    'psg': psg,
    'Celtic': celtic,
    'celtic': celtic,
    'CELTIC': celtic,
    'Atletico Madrid': atleticoMadrid,
    'atletico madrid': atleticoMadrid,
    'ATLETICO MADRID': atleticoMadrid,
    'Benfica': benfica,
    'benfica': benfica,
    'BENFICA': benfica,
    'Brighton': brighton,
    'brighton': brighton,
    'BRIGHTON': brighton,
    'Newcastle': newcastle,
    'newcastle': newcastle,
    'NEWCASTLE': newcastle,
    'Aston Villa': astonVilla,
    'aston villa': astonVilla,
    'ASTON VILLA': astonVilla,
    'Wolves': wolves,
    'wolves': wolves,
    'WOLVES': wolves,
    'juventus': juventus,
    'JUVENTUS': juventus,
    'Juventus': juventus,
};

export const getLogo = (clubName) => {
    return logos[clubName] || null; 
};
