import React, { useState } from "react";
import api from './api.js'; // Axios instance for API calls

const App = () => {
  const [season, setSeason] = useState(""); // Input for the season
  const [stats, setStats] = useState(null); // Overall stats
  const [matches, setMatches] = useState(null); // Season matches
  const [error, setError] = useState(null); // For error handling

  const handleFetchData = async () => {
    setError(null); // Clear any previous errors
    setStats(null);
    setMatches(null);

    try {
      // Fetch overall stats
      const statsResponse = await api.get(
        `http://localhost:8000/overall_stats/`,
        { params: { season } }
      );
      setStats(statsResponse.data);

      // Fetch season matches
      const matchesResponse = await api.get(
        `http://localhost:8000/season_matches/`,
        { params: { season } }
      );
      setMatches(matchesResponse.data);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>LeBron James Data Viewer</h1>
      <div>
        <label>
          Enter Season (e.g., "2023-2024"):
          <input
            type="text"
            value={season}
            onChange={(e) => setSeason(e.target.value)}
          />
        </label>
        <button onClick={handleFetchData} disabled={!season.trim()}>
          Fetch Data
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {stats && (
        <div>
          <h2>Overall Stats</h2>
          <table border="1" style={{ width: "100%", textAlign: "left" }}>
            <thead>
              <tr>
                <th>YEAR</th>
                <th>FG%</th>
                <th>3P%</th>
                <th>FT%</th>
                <th>REB</th>
                <th>AST</th>
                <th>PTS</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((stat, index) => {
                const [year, fg, threeP, ft, reb, ast, pts] = stat.split(", ");
                return (
                  <tr key={index}>
                    <td>{year}</td>
                    <td>{fg}</td>
                    <td>{threeP}</td>
                    <td>{ft}</td>
                    <td>{reb}</td>
                    <td>{ast}</td>
                    <td>{pts}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {matches && (
        <div>
          <h2>Season Matches</h2>
          <table border="1" style={{ width: "100%", textAlign: "left" }}>
            <thead>
              <tr>
                <th>DATE</th>
                <th>HOME-TEAM</th>
                <th>OPP-TEAM</th>
                <th>RESULT</th>
                <th>REB</th>
                <th>AST</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((match, index) => {
                const [
                  season,
                  homeTeam,
                  oppTeam,
                  result,
                  reb,
                  ast,
                ] = match.split(", ");
                return (
                  <tr key={index}>
                    <td>{season}</td>
                    <td>{homeTeam}</td>
                    <td>{oppTeam}</td>
                    <td>{result}</td>
                    <td>{reb}</td>
                    <td>{ast}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default App;
