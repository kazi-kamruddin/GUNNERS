import { useState } from "react";
import { useLogin } from "../hook/useLogin";
import "../allCss/achievements.css";
import { useNavigate } from 'react-router-dom';

const Achievements = () => {
  return (
    <div className="container">
        <div className="service-wrapper">
            <div className="service">
                <h1 className="achievement-title"> HONOURS </h1>
                <div className="cards-achieve">
                    <div className="card-achieve">
                      
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                        />
                        <h2> UEFA CHAMPIONS LEAGUE</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                    <div className="card-achieve">
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                          className="img-style"
                        />
                        <h2> UEFA CHAMPIONS LEAGUE</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                    <div className="card-achieve">
                        
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                        />
                        <h2> F.A Cup(14)</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                    <div className="card-achieve">
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                        />
                        <h2> LEAGUE CUP(2)</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                    <div className="card-achieve">
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                        />
                        <h2> EUROPEAN FAIRS CUP(1)</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                    <div className="card-achieve">
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                        />
                        <h2>CHARITY/COMMUNITY SHIELD(16+1 SHARED)</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                    <div className="card-achieve">
                        <img 
                          src="E:\GUNNERS\frontEnd\src\assets\achivementsAssets\UCL.jpg" 
                        />
                        <h2> UEFA CHAMPIONS LEAGUE</h2>
                        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Distinctio corrupti aliquid illo eveniet non earum, ratione natus delectus 
                            eligendi fuga nemo aut, ad quis culpa cum recusandae. Ducimus, eos fuga!
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};

export default Achievements;
