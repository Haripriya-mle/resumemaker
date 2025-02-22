import { useState, useEffect } from "react";
import { 
  Button, TextField, Container, Typography, Box, 
  Input, Switch, CssBaseline, ThemeProvider, createTheme 
} from "@mui/material";

export default function ResumeGenerator() {
  const [formData, setFormData] = useState({
    name: "",
    experience: "",
    skills: "",
    education: "",
    job_description: "",
  });
  const [resumeData, setResumeData] = useState(null);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("darkMode") === "true");

  useEffect(() => {
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
    },
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const generateResume = async () => {
    const response = await fetch("http://127.0.0.1:8000/generate_resume/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    const data = await response.json();
    setResumeData(data.resume);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const uploadData = new FormData();
    uploadData.append("resume_file", file);

    const response = await fetch("http://127.0.0.1:8000/parse_resume/", {
      method: "POST",
      body: uploadData,
    });

    const data = await response.json();
    setFormData(data.parsed_resume);
  };

  const downloadResume = async () => {
  if (!resumeData) {
    console.error("Error: No resume data available");
    return;
  }
  console.log("Resume data being sent to download:", resumeData); // Debugging log
  console.log("Resume data kjhhhhhhhhhhhhhhhhhhhhhh sent to download:");
  try {
    const response = await fetch("http://127.0.0.1:8000/generate_resume2/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),  // Use resumeData instead of formData
    });

    if (!response.ok) throw new Error("Failed to download");

    const blob = await response.blob();
    if (!blob) {
      console.error("Error: Empty PDF response");
      return;
    }
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "resume.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Download error:", error);
  }
};



  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm" sx={{ p: 3, borderRadius: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h4" gutterBottom>
            ATS Resume Generator
          </Typography>
          <Switch checked={darkMode} onChange={() => setDarkMode(!darkMode)} />
        </Box>
        



          
        <Box component="form" display="flex" flexDirection="column" gap={2}>
          <Input type="file" onChange={handleFileUpload} accept=".pdf,.doc,.docx" />
          <TextField label="Full Name" name="name" value={formData.name} onChange={handleChange} fullWidth />
          <TextField label="Phone" name="phone" value={formData.phone} onChange={handleChange} fullWidth />
          <TextField label="Email" name="email" value={formData.email} onChange={handleChange} fullWidth />
          <TextField label="LinkedIn" name="linkedin" value={formData.linkedin} onChange={handleChange} fullWidth />
          <TextField label="Portfolio/Website" name="website" value={formData.website} onChange={handleChange} fullWidth />
          <TextField label="Profile Summary" name="summary" value={formData.summary} onChange={handleChange} fullWidth multiline rows={3} />
          <TextField label="Work Experience" name="experience" value={formData.experience} onChange={handleChange} fullWidth multiline rows={4} />
          <TextField label="Skills" name="skills" value={formData.skills} onChange={handleChange} fullWidth multiline rows={2} />
          <TextField label="Education" name="education" value={formData.education} onChange={handleChange} fullWidth multiline rows={2} />
          <TextField label="Certifications" name="certifications" value={formData.certifications} onChange={handleChange} fullWidth multiline rows={2} />
           <TextField label="Job Description" name="job_description" value={formData.job_description} onChange={handleChange} fullWidth multiline rows={3} />
          <Button variant="contained" color="primary" onClick={generateResume}>
            Generate Resume
          </Button>
        </Box>
                  
        {resumeData && (
          <Box mt={3} p={2} borderRadius={2}>
            <Typography variant="h5">{resumeData.name}</Typography>
            <Typography variant="subtitle1"><strong>Summary:</strong> {resumeData.summary}</Typography>
            <Typography variant="body1"><strong>Experience:</strong> {resumeData.experience}</Typography>
            <Typography variant="body1"><strong>Skills:</strong> {resumeData.skills}</Typography>
            <Typography variant="body1"><strong>Education:</strong> {resumeData.education}</Typography>

            <Button variant="contained" color="secondary" onClick={downloadResume} sx={{ mt: 2 }}>
              Download Resume
            </Button>
          </Box>
        )}
      </Container>
    </ThemeProvider>
  );
}
