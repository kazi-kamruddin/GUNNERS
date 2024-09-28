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
                        
                        <h2> EUROPEAN</h2>
                        <h3> 1</h3>
                        <p>
                        Arsenal has a long history in European competitions, though they've never won the UEFA Champions League. Their closest attempt came in 2006 when they reached the final but lost to Barcelona. They have won the UEFA Cup Winners' Cup in 1994 and reached the finals of the UEFA Europa League twice, in 2000 and 2019. Despite these near misses, they remain one of Europe's top clubs. Arsenal continues to compete regularly in European tournaments.
                        </p>
                    </div>
                    <div className="card-achieve">        
                        
                        <h2> Premier League </h2>
                        <h3> 13</h3>
                        <p>
                          Arsenal Football Club has a rich history in the Premier League, having won the title 13 times in total (including titles from the old First Division). In the Premier League era, which began in 1992, Arsenal has secured the title three times
                        </p>
                    </div>

                    <div className="card-achieve">
                        
                        <h2> LEAGUE CUP</h2>
                        <h3>2</h3>
                        <p>
                        Arsenal has had a successful history in the EFL Cup, also known as the League Cup. The Gunners have won the trophy twice, in 1987 and 1993, showcasing their ability to perform well in knockout competitions. Their victory in 1993 was particularly memorable as they secured a unique double by winning both the League Cup and the FA Cup in the same season. 
                        </p>
                    </div>
                    <div className="card-achieve">
                        
                        <h2> FA CUP</h2>
                        <h3> 14 </h3>
                        <p>
                        Arsenal is the most successful club in FA Cup history, having won the prestigious tournament 14 times. Their victories span several decades, with notable triumphs in 1971, 1993, and 2014, showcasing the club's enduring legacy in English football. 
                        </p>
                    </div>

                    <div className="card-achieve">
                        
                        <h2> COMMUNITY SHIELD</h2>
                        <h3> 16 </h3>
                        <p>
                        The Community Shield, often referred to as the Charity Shield, is an annual football match held in England between the winners of the Premier League and the FA Cup. Established in 1908, it serves as a curtain-raiser for the new football season. The match is played at Wembley Stadium and typically occurs in early August. Proceeds from the event often go to charity, emphasizing its community-focused spirit. 
                        </p>
                    </div>

                  
                </div>
            </div>
        </div>
    </div>
  );
};

export default Achievements;
