import { Link } from "expo-router";
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";
export default function Workspace(){
 return <SafeAreaView style={s.safe}><ScrollView contentContainerStyle={s.wrap}>
  <Link href="/" style={s.back}>← N1MOX30</Link>
  <Text style={s.title}>Workspace</Text>
  {["Assistant","Create","Automation","Publishing","Analytics","Growth","Accounts"].map(x=><View style={s.row} key={x}><Text style={s.name}>{x}</Text><Text style={s.status}>Ready</Text></View>)}
 </ScrollView></SafeAreaView>
}
const s=StyleSheet.create({safe:{flex:1,backgroundColor:"#090b10"},wrap:{padding:24,paddingTop:40},back:{color:"#8b9cff",marginBottom:20},title:{color:"#fff",fontSize:32,fontWeight:"800",marginBottom:22},row:{padding:18,borderRadius:14,borderWidth:1,borderColor:"#222b3a",backgroundColor:"#111722",marginBottom:10,flexDirection:"row",justifyContent:"space-between"},name:{color:"#fff",fontSize:16,fontWeight:"700"},status:{color:"#6ee7b7"}})
