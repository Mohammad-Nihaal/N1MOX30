import { Link } from "expo-router";
import { Pressable, SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

const cards = [
  ["AI Assistant","Run creator commands by text or voice."],
  ["Content Studio","Research → script → voice → video → thumbnail."],
  ["Automation","Build and monitor repeatable workflows."],
  ["Publishing","Distribute to YouTube, Instagram, TikTok and X."],
  ["Analytics","See cross-platform creator performance."],
  ["Growth","Turn performance data into next actions."]
];

export default function Home(){
  return <SafeAreaView style={s.safe}><ScrollView contentContainerStyle={s.wrap}>
    <Text style={s.kicker}>N1MOX30</Text><Text style={s.title}>Creator Operating System</Text>
    <Text style={s.sub}>One workspace for intelligence, production, automation and publishing.</Text>
    <Link href="/workspace" asChild><Pressable style={s.cta}><Text style={s.ctaText}>Open workspace</Text></Pressable></Link>
    <View style={s.grid}>{cards.map(([title,desc])=><View style={s.card} key={title}><Text style={s.cardTitle}>{title}</Text><Text style={s.cardText}>{desc}</Text></View>)}</View>
  </ScrollView></SafeAreaView>
}
const s=StyleSheet.create({
 safe:{flex:1,backgroundColor:"#090b10"},wrap:{padding:24,paddingTop:48},
 kicker:{color:"#8b9cff",fontWeight:"800",letterSpacing:2},title:{color:"#fff",fontSize:36,fontWeight:"800",marginTop:8},sub:{color:"#9ca6b8",fontSize:16,lineHeight:24,marginTop:12},
 cta:{backgroundColor:"#6673ff",padding:16,borderRadius:14,marginTop:24,alignItems:"center"},ctaText:{color:"#fff",fontWeight:"800"},
 grid:{gap:12,marginTop:28},card:{backgroundColor:"#111722",borderWidth:1,borderColor:"#222b3a",borderRadius:16,padding:18},cardTitle:{color:"#fff",fontSize:17,fontWeight:"700"},cardText:{color:"#8e99aa",marginTop:7,lineHeight:20}
});
