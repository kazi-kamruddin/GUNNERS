import React from 'react';
import '../allCss/footer.css';

import { CgAdidas } from "react-icons/cg";
import { SiEmirates, SiMg, SiPremierleague, SiKonami, SiBarclays, SiVolkswagen, SiTesla, SiTrivago, SiFord, SiFifa } from "react-icons/si";
import { RiPixelfedFill } from "react-icons/ri";
import { IoLogoGoogle } from "react-icons/io5";
import { FaFacebook } from "react-icons/fa";
import { FaSquareXTwitter } from "react-icons/fa6";
import { FaSnapchat } from "react-icons/fa";
import { FaTwitch } from "react-icons/fa";
import { RiInstagramFill } from "react-icons/ri";
import { FaYoutube } from "react-icons/fa";
import { FaPix } from "react-icons/fa6";
import { BsSinaWeibo } from "react-icons/bs";



const Footer = () => {
  return (
    <footer className='foot'>
      <div className="footer-logos">

        <div className="footer-row-social">
          <a href="https://www.facebook.com/Arsenal/"><FaFacebook /></a>
          <a href="https://x.com/Arsenal?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Eauthor"><FaSquareXTwitter/></a>
          <a href="https://www.twitch.tv/arsenal"><FaTwitch/></a>
          <a href="https://www.snapchat.com/add/officialafc"><FaSnapchat/></a>
        </div>

        <div className="footer-row-social">
          <a href="https://www.instagram.com/arsenal/?hl=en"><RiInstagramFill /></a>
          <a href="https://www.youtube.com/channel/UCpryVRk_VDudG8SHXgWcG0w"><FaYoutube/></a>
          <a href="https://www.pixstory.com/search/?search=arsenal"><FaPix/></a>
          <a href="#"><BsSinaWeibo/></a>
        </div>
        <br />
        <hr className="footer-divider" />
        <br />  
        <div className="footer-row">
          <a href="https://www.adidas.com/us"><CgAdidas /></a>
          <a href="https://www.emirates.com/"><SiEmirates/></a>
          <a href="https://www.mg.co.uk/"><SiMg/></a>
          <a href="https://www.premierleague.com/"><SiPremierleague/></a>
        </div>

        <div className="footer-row-mid">
          <a href="https://www.barclays.co.uk/"><SiBarclays/></a>
          <a href="https://www.tesla.com/"><SiTesla/></a>
          <a href="https://my1.konami.net/"><SiKonami/></a>
          <a href="https://store.google.com/category/phones"><RiPixelfedFill/></a>
          <a href="https://www.vw.com/en.html"><SiVolkswagen/></a>
        </div>

        <div className="footer-row">
          <a href="https://www.trivago.com/"><SiTrivago/></a>
          <a href="https://www.ford.com/"><SiFord/></a>
          <a href="https://www.fifa.com/"><SiFifa/></a>
          <a href="https://www.google.co.uk/"><IoLogoGoogle/></a>
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
