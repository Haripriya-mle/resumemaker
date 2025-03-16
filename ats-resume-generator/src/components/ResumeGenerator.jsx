import { useState, useEffect } from "react";
import { 
  Button, TextField, Container, Typography, Box, 
  Input, Switch, CssBaseline, ThemeProvider, createTheme, Paper
} from "@mui/material";
import Grid from "@mui/material/Grid";  
import { PDFDownloadLink } from "@react-pdf/renderer";
import ResumePDF from "./ResumePDF";

export default function ResumeGenerator() {
  const [formData, setFormData] = useState({
    name: "",
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
    console.log("form data after upload:", formData);
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

  

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth={false} sx={{ minHeight: "100vh", p: 4, backgroundColor: darkMode ? "#121212" : "#f5f5f5" }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" color="primary">ATS Resume Generator</Typography>
          <Switch checked={darkMode} onChange={() => setDarkMode(!darkMode)} />
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
              
                        <Input type="file" onChange={handleFileUpload} accept=".pdf,.doc,.docx" />
              <Typography variant="h6" mb={2}>Enter Your Details</Typography>
              <Box component="form" display="flex" flexDirection="column" gap={2}>
                
                <TextField label="Full Name" name="name" value={formData.name} onChange={handleChange} fullWidth />
                <TextField label="Phone" name="phone" value={formData.phone} onChange={handleChange} fullWidth />
                <TextField label="Email" name="email" value={formData.email} onChange={handleChange} fullWidth />
                <TextField label="LinkedIn" name="linkedin" value={formData.linkedin} onChange={handleChange} fullWidth />
                <TextField label="Portfolio/Website" name="website" value={formData.website} onChange={handleChange} fullWidth />
                <TextField label="Work Experience" name="experience" value={formData.experience} onChange={handleChange} fullWidth multiline rows={4} />
                <TextField label="Skills" name="skills" value={formData.skills} onChange={handleChange} fullWidth multiline rows={2} />
                <TextField label="projects" name="projects" value={formData.projects} onChange={handleChange} fullWidth multiline rows={2} />
                
                <TextField label="Certifications" name="certifications" value={formData.certifications} onChange={handleChange} fullWidth multiline rows={2} />
                <TextField label="Job Description" name="job_description" value={formData.job_description} onChange={handleChange} fullWidth multiline rows={3} />
                
                <TextField label="Education" name="education" value={formData.education} onChange={handleChange} fullWidth multiline rows={2} />
               <Button variant="contained" color="primary" onClick={generateResume} fullWidth>Generate Resume</Button>
              </Box>
            </Paper>
          </Grid>

          {resumeData && (
            <Grid item xs={12} md={8}>
              <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
                <Typography variant="h5" mb={2}>{resumeData.name}</Typography>
                <Typography variant="subtitle1" mb={1}><strong>Summary:</strong> {resumeData.summary}</Typography>
                <Typography variant="body1" mb={1}><strong>Experience:</strong> {resumeData.experience}</Typography>
                <Typography variant="body1" mb={1}><strong>Skills:</strong> {resumeData.skills}</Typography>
                <Typography variant="body1" mb={1}><strong>Education:</strong> {resumeData.education}</Typography>
                
                <Typography variant="body1" mb={1}><strong>projects:</strong> {resumeData.projects}</Typography>
                <Typography variant="body1" mb={1}><strong>certifications:</strong> {resumeData.certifications}</Typography>
                {resumeData.cover_letter && (
                  <Typography variant="body1" mb={1}><strong>Cover Letter:</strong> {resumeData.cover_letter}</Typography>
                )}
                <PDFDownloadLink document={<ResumePDF resumeData={resumeData} />} fileName="resume.pdf">
        {({ loading }) => (
          <Button variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            {loading ? "Generating PDF..." : "Download Resume"}
          </Button>
        )}
      </PDFDownloadLink>
              </Paper>
            </Grid>
          )}
        </Grid>
       
      </Container>
    </ThemeProvider>
  );
}
