import { Page, Text, View, Document, StyleSheet, Font } from '@react-pdf/renderer';

// Register fonts
Font.register({ family: 'Times-Roman', src: 'https://fonts.gstatic.com/s/timesnewroman/v14/QldKNThLqRwH-OJ1UHjlKGlW5qhExmQ.ttf' });

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 11,
    fontFamily: 'Times-Roman',
  },
  header: {
    fontSize: 20,
    textAlign: 'center',
    fontWeight: 'bold',
    marginBottom: 10,
  },
  contact: {
    fontSize: 11,
    textAlign: 'center',
    marginBottom: 20,
  },
  section: {
    marginBottom: 10,
  },
  bold: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 3,
  },
  text: {
    fontSize: 11,
  },
  divider: {
    borderBottomWidth: 1,
    borderBottomColor: '#000',
    marginVertical: 5,
  },
});

const ResumeDocument = ({ resumeData }) => (
  <Document>
    <Page style={styles.page}>
      <Text style={styles.header}>{resumeData.name}</Text>
      <Text style={styles.contact}>{resumeData.phone} | {resumeData.email} | {resumeData.linkedin} | {resumeData.website}</Text>
      
      <View style={styles.section}>
        <Text style={styles.bold}>Summary</Text>
        <View style={styles.divider} />
        <Text style={styles.text}>{resumeData.summary}</Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.bold}>Experience</Text>
        <View style={styles.divider} />
        <Text style={styles.text}>{resumeData.experience}</Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.bold}>Skills</Text>
        <View style={styles.divider} />
        <Text style={styles.text}>{resumeData.skills}</Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.bold}>Projects</Text>
        <View style={styles.divider} />
        <Text style={styles.text}>{resumeData.projects}</Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.bold}>Certifications</Text>
        <View style={styles.divider} />
        <Text style={styles.text}>{resumeData.certifications}</Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.bold}>Education</Text>
        <View style={styles.divider} />
        <Text style={styles.text}>{resumeData.education}</Text>
      </View>
    </Page>
  </Document>
);

export default ResumeDocument;
