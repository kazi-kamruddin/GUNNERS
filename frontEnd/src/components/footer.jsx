  import React from 'react';
  import '../allCss/footer.css';

  import { CgAdidas } from "react-icons/cg";
  import { SiEmirates } from "react-icons/si";
  import { SiMg } from "react-icons/si";
  import { SiPremierleague } from "react-icons/si";
  import { SiKonami } from "react-icons/si";
  import { RiPixelfedFill } from "react-icons/ri";
  import { SiBarclays } from "react-icons/si";
  import { SiVolkswagen } from "react-icons/si";
  import { SiTesla } from "react-icons/si";
  import { SiTrivago } from "react-icons/si";
  import { SiFord } from "react-icons/si";
  import { SiFifa } from "react-icons/si";
  import { IoLogoGoogle } from "react-icons/io5";

  const Footer = () => {
    return (
      <footer>
        <div className="footer-logos">
          <div className="footer-row">
            
            <a href="#"><CgAdidas /></a>
            <a href="#"><SiEmirates/></a>
            <a href="#"><SiMg/></a>
            <a href="#"><SiPremierleague  /></a>
            
          
          </div>
          <div className="footer-row-mid">
            <a href="#"><SiBarclays/></a>
            <a href="#"><SiTesla /></a>
            <a href="#"><SiKonami/></a>
            <a href="#"><RiPixelfedFill/></a>
            <a href="#"><SiVolkswagen/></a>
          </div>
        
          <div className="footer-row">
            <a href="#"><SiTrivago /></a>
            <a href="#"><SiFord /></a>
            <a href="#"><SiFifa /></a>
            <a href="#"><IoLogoGoogle /></a>
          </div>
        </div>

        <div className="footer-links">
          <a href="#">Terms of Use</a>
          <a href="#">Privacy Policy</a>
          <a href="#">Cookie Policy</a>
          <a href="#">Website Accessibility Statement</a>
          <a href="#">Inviqa</a>
        </div>
      </footer>
    );
  };

  export default Footer;
