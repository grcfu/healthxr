"use client";
import { motion } from "framer-motion";
import { 
  Activity, ShieldCheck, Eye, Zap, MapPin, 
  ChevronRight, ArrowUpRight, Globe, Layers, 
  User, Database, Stethoscope, BrainCircuit,
  Briefcase, Mail, Code
} from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#F8FAFC] text-[#0F172A] overflow-x-hidden selection:bg-cyan-100">
      
      {/* --- DYNAMIC BACKGROUND ORCHESTRATION --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-enamel/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-electric/10 blur-[120px] rounded-full" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
      </div>

      {/* --- STICKY HUD NAVIGATION --- */}
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-5xl">
        <div className="glass-panel px-8 py-4 rounded-full flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-enamel animate-ping" />
            <div className="font-bold text-xl tracking-tighter uppercase">Health<span className="text-enamel">XR</span></div>
          </div>
          <div className="hidden md:flex gap-10 text-[10px] uppercase tracking-[0.2em] font-black text-slate-400">
            <a href="#technology" className="hover:text-enamel transition-colors">Tech</a>
            <a href="#strategy" className="hover:text-enamel transition-colors">Strategy</a>
            <a href="#founder" className="hover:text-enamel transition-colors">Founder</a>
            <a href="#careers" className="hover:text-enamel transition-colors">Careers</a>
          </div>
          <button className="bg-radiology text-white text-[10px] font-black uppercase tracking-widest px-6 py-2.5 rounded-full hover:bg-enamel transition-all">
            Secure Portal
          </button>
        </div>
      </nav>

      {/* --- HERO: THE OUTCOME-FIRST COMMAND --- */}
      <section className="relative z-10 pt-48 pb-32 px-6 text-center max-w-6xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
           <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-panel text-enamel text-[10px] font-black uppercase tracking-[0.3em]">
            <Activity className="w-3 h-3" /> System Live // St. Louis Cluster
          </span>
          
          <h1 className="text-7xl md:text-[10rem] font-black tracking-tighter mb-8 leading-[0.85] uppercase">
            Clinical <br /><span className="text-enamel italic">Autopilot.</span>
          </h1>
          
          <div className="max-w-2xl mx-auto space-y-8">
            <p className="text-xl text-slate-500 font-medium leading-relaxed">
              Transforming clinical encounters into <span className="text-radiology font-bold">structured intelligence</span> through real-time multimodal analysis.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button className="bg-radiology text-white px-10 py-5 rounded-2xl font-black text-xs uppercase tracking-widest hover:shadow-2xl hover:shadow-enamel/20 transition-all flex items-center justify-center gap-2">
                Initialize Pilot <ChevronRight className="w-4 h-4" />
              </button>
              <div className="glass-panel px-10 py-5 rounded-2xl font-black text-xs uppercase tracking-widest text-slate-400 flex items-center justify-center gap-2">
                <MapPin className="w-4 h-4" /> HQ: St. Louis, MO
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* --- THE BENTO GRID: MULTIMODAL CAPABILITY --- */}
      <section id="technology" className="relative z-10 py-20 px-6 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div className="md:col-span-2 glass-panel p-12 rounded-[3rem] relative overflow-hidden group">
            <div className="relative z-10 space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-enamel/10 flex items-center justify-center text-enamel">
                <Eye className="w-6 h-6" />
              </div>
              <h3 className="text-4xl font-black tracking-tight uppercase">Visual Intelligence</h3>
              <p className="text-slate-500 text-lg max-w-md">
                Health XR analyzes non-verbal clinical cues to capture the full procedural context that audio-only scribes miss, delivering high-fidelity clinical documentation.
              </p>
            </div>
            <div className="absolute bottom-0 right-0 w-64 h-64 bg-enamel/5 rounded-full blur-3xl group-hover:bg-enamel/10 transition-colors" />
          </div>

          <div className="glass-panel p-12 rounded-[3rem] flex flex-col justify-between border-mint/20">
            <ShieldCheck className="w-10 h-10 text-mint" />
            <div className="space-y-4">
              <h4 className="text-xl font-black uppercase">Privacy-First</h4>
              <p className="text-slate-500 text-sm">Automated face-blurring and audio processing designed to support HIPAA-compliant data workflows.</p>
            </div>
          </div>

          <div className="glass-panel p-12 rounded-[3rem] space-y-6">
            <Zap className="w-10 h-10 text-electric" />
            <h4 className="text-xl font-black uppercase tracking-tighter">Revenue Integrity</h4>
            <p className="text-slate-500 text-sm">Generating defensible records for high-volume procedural specialties to strengthen revenue cycle compliance.</p>
          </div>

          <div className="md:col-span-2 glass-panel p-12 rounded-[3rem] flex flex-col md:flex-row items-center gap-12">
            <div className="flex-1 space-y-6">
              <Globe className="w-10 h-10 text-enamel" />
              <h4 className="text-xl font-black uppercase">Clinical Growth</h4>
              <p className="text-slate-500 text-sm leading-relaxed">Enabling real-time translation and clinical decision support directly within the provider workflow.</p>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-4">
              <div className="p-6 rounded-2xl bg-slate-50 text-center">
                <div className="text-3xl font-black text-radiology">40%</div>
                <div className="text-[8px] uppercase font-bold text-slate-400">Documentation Efficiency</div>
              </div>
              <div className="p-6 rounded-2xl bg-slate-50 text-center">
                <div className="text-3xl font-black text-radiology">$16B</div>
                <div className="text-[8px] uppercase font-bold text-slate-400">Market Potential</div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* --- STRATEGY SECTION: THE $15.9B VISION --- */}
      <section id="strategy" className="relative z-10 py-32 px-6 max-w-7xl mx-auto">
        <div className="bg-radiology rounded-[4rem] p-12 md:p-24 text-white relative overflow-hidden">
          <div className="relative z-10 grid md:grid-cols-2 gap-20 items-center">
            <div className="space-y-10">
              <span className="text-enamel font-bold text-xs uppercase tracking-[0.4em]">Strategic Roadmap</span>
              <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase leading-none">Solving <br/>Outpatient <br/>Burnout.</h2>
              <p className="text-slate-400 text-xl leading-relaxed">
                Initially targeting the U.S. digital dentistry market, projected to reach <span className="text-white font-bold">$15.9B by 2032</span>. Validating across high-volume dental groups and multi-site networks.
              </p>
              <div className="flex gap-4">
                <div className="px-6 py-3 rounded-full border border-white/10 text-[10px] font-bold uppercase tracking-widest text-enamel">
                  Pilot Phase
                </div>
                <div className="px-6 py-3 rounded-full border border-white/10 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                  SaaS Deployment
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute -inset-10 bg-enamel/20 blur-[100px] rounded-full" />
              <div className="glass-panel p-10 rounded-[2.5rem] bg-white/5 border-white/10 relative z-10">
                <Layers className="w-10 h-10 text-electric mb-6" />
                <h4 className="text-2xl font-black uppercase mb-4 tracking-tighter">Multimodal Engine</h4>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Leveraging proprietary AI models to analyze procedural data and understand complex clinical nuance.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FOUNDER PROFILE: THE HEART OF TRUST --- */}
      <section id="founder" className="relative z-10 py-32 px-6 max-w-5xl mx-auto text-center space-y-16">
        <div className="space-y-4">
          <span className="text-enamel font-bold text-xs uppercase tracking-[0.4em]">The Leadership</span>
          <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase leading-tight">Built by a Clinician <br/>Who Lives the Problem.</h2>
        </div>

        <div className="grid md:grid-cols-3 gap-12 text-left items-center">
          <div className="space-y-8">
            <div className="space-y-2">
              <h4 className="font-black uppercase tracking-widest text-xs text-slate-400">Clinical Focus</h4>
              <p className="text-xl font-bold italic">High-volume systems and procedural specialties</p>
            </div>
            <div className="space-y-2">
              <h4 className="font-black uppercase tracking-widest text-xs text-slate-400">Background</h4>
              <p className="text-xl font-bold">UMKC School of Dentistry</p>
            </div>
          </div>

          <div className="relative flex justify-center group">
            {/* This adds the glowing border that activates on hover */}
            <div className="absolute -inset-2 rounded-[3.5rem] bg-gradient-to-r from-enamel via-electric to-mint opacity-0 group-hover:opacity-100 blur-lg transition-opacity duration-500 z-0" />
            
            <div className="w-64 h-64 rounded-[3rem] glass-panel flex items-center justify-center relative overflow-hidden group border-white/10 z-10">
              {/* 📸 PLACE YOUR IMAGE ADDRESS BELOW */}
              <img 
                src="https://www.sihf.org/media-library/profile-photos/804-1741212682.jpg" 
                alt="Dr. Aaron DeForest" 
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
              />
              
              {/* Subtle text overlay at the bottom of the photo */}
              <div className="absolute bottom-0 left-0 w-full text-center bg-radiology/80 backdrop-blur-sm py-3">
                <div className="text-[10px] font-black uppercase tracking-widest text-enamel">Founder // CEO</div>
              </div>
            </div>
          </div>

          <div className="space-y-8 text-right">
             <p className="text-slate-500 leading-relaxed italic border-r-2 border-enamel pr-6">
              "We're engineering the clinical intelligence tool I wish I had every day in high-volume networks."
             </p>
             <div>
                <p className="font-black text-radiology uppercase tracking-tighter">Aaron DeForest, DDS</p>
                <p className="text-slate-400 text-xs">St. Louis Startup Ecosystem</p>
             </div>
          </div>
        </div>
      </section>

      {/* --- CAREER PORTAL --- */}
      <section id="careers" className="relative z-10 py-32 px-6 max-w-7xl mx-auto">
        <div className="text-center mb-20 space-y-4">
          <span className="text-enamel font-bold text-xs uppercase tracking-[0.4em]">The Engineering Team</span>
          <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase">Join the <br/>Build.</h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 glass-panel p-12 rounded-[3rem] border-enamel/20 relative overflow-hidden">
            <div className="flex justify-between items-start mb-10">
              <div className="space-y-2">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-enamel/10 text-enamel text-[10px] font-black uppercase tracking-widest">
                  <Activity className="w-3 h-3" /> Summer 2026
                </div>
                <h3 className="text-4xl font-black uppercase tracking-tight">Software Engineer Intern</h3>
                <p className="text-slate-400 font-bold text-sm uppercase">Computer Vision & AI Pipeline Focus</p>
              </div>
              <div className="text-right">
                <div className="text-[10px] font-black uppercase text-slate-300 mb-1">Status</div>
                <div className="text-xs font-bold text-mint uppercase tracking-widest font-mono">Position Filled</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-12">
              <div className="space-y-6">
                <h4 className="text-xs font-black uppercase tracking-widest text-radiology">Scope of Work</h4>
                <ul className="space-y-4 text-sm text-slate-500 leading-relaxed">
                  <li className="flex gap-3"><Code className="w-4 h-4 text-enamel shrink-0"/> Architecting real-time anonymization pipelines for clinical video processing.</li>
                  <li className="flex gap-3"><Code className="w-4 h-4 text-enamel shrink-0"/> Developing clinician-facing XR visualization and interface tools.</li>
                  <li className="flex gap-3"><Code className="w-4 h-4 text-enamel shrink-0"/> Implementing secure audio-anonymization and HIPAA-compliant data routing.</li>
                </ul>
              </div>
              <div className="space-y-6">
                <h4 className="text-xs font-black uppercase tracking-widest text-radiology">Core Competencies</h4>
                <ul className="space-y-4 text-sm text-slate-500 leading-relaxed">
                  <li className="flex gap-3"><ChevronRight className="w-4 h-4 text-enamel shrink-0"/> Advanced proficiency in Python (AI/ML) and TypeScript.</li>
                  <li className="flex gap-3"><ChevronRight className="w-4 h-4 text-enamel shrink-0"/> Experience with modern Computer Vision and deep learning frameworks.</li>
                  <li className="flex gap-3"><ChevronRight className="w-4 h-4 text-enamel shrink-0"/> Strong alignment with healthcare innovation and data security.</li>
                </ul>
              </div>
            </div>

            <div className="mt-12 pt-10 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="flex items-center gap-4">
                 <div className="p-3 rounded-xl bg-slate-50 text-slate-400"><Briefcase className="w-5 h-5"/></div>
                 <div>
                    <p className="text-[10px] font-black uppercase text-slate-300">Application Cycle</p>
                    <p className="text-xs font-bold text-radiology">Closed: February 2, 2026</p>
                 </div>
              </div>
              <p className="text-[10px] font-medium text-slate-400 italic">Role verified for 2026 Summer Cohort.</p>
            </div>
          </div>

          <div className="glass-panel p-10 rounded-[3rem] bg-radiology text-white border-white/5 flex flex-col justify-between">
            <div className="space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-enamel/20 flex items-center justify-center text-enamel">
                <Mail className="w-6 h-6" />
              </div>
              <h4 className="text-2xl font-black uppercase tracking-tighter">Inquiries & <br/>Verification</h4>
              <p className="text-slate-400 text-sm leading-relaxed">
                For internship verification or employment inquiries, please submit your formal request and CV to the Founder.
              </p>
            </div>
            
            <div className="space-y-4 pt-10">
              <div className="p-6 rounded-[2rem] bg-white/5 border border-white/10 hover:border-enamel transition-all group">
                 <p className="text-[10px] font-black uppercase tracking-[0.2em] text-enamel mb-2">Primary Inquiries</p>
                 <p className="text-xs font-bold group-hover:text-enamel transition-colors truncate">aaron@healthxr.ai</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FOOTER: THE ECOSYSTEM --- */}
      <footer className="relative z-10 border-t border-slate-100 bg-white/80 backdrop-blur-xl pt-32 pb-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-20 mb-32">
            <div className="col-span-2 space-y-8">
              <div className="font-bold text-4xl tracking-tighter uppercase">Health<span className="text-enamel">XR</span></div>
              <p className="text-slate-400 max-w-sm leading-relaxed text-lg">
                The clinical autopilot for high-volume healthcare environments.
              </p>
              <div className="flex gap-4">
                <button className="p-4 rounded-2xl bg-radiology text-white hover:bg-enamel transition-colors"><ArrowUpRight className="w-5 h-5"/></button>
                <div className="p-4 rounded-2xl glass-panel text-slate-400 flex items-center gap-3 px-6 border-mint/20">
                  <span className="w-2 h-2 rounded-full bg-mint" /> 
                  <span className="text-[10px] font-black uppercase tracking-widest">HIPAA-Compliant Architecture</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-8">
              <h5 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-300">Ecosystem</h5>
              <ul className="space-y-4 font-bold text-slate-500">
                <li className="hover:text-enamel transition-colors">Arch Grants</li>
                <li className="hover:text-enamel transition-colors">Washington University</li>
                <li className="hover:text-enamel transition-colors">Skandalaris Center</li>
              </ul>
            </div>

            <div className="space-y-8">
              <h5 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-300">Core Engine</h5>
              <ul className="space-y-4 font-bold text-slate-500 text-sm">
                <li className="flex gap-2 items-center"><Database className="w-4 h-4 text-enamel"/> Privacy-First Processing</li>
                <li className="flex gap-2 items-center"><Stethoscope className="w-4 h-4 text-enamel"/> Procedural Computer Vision</li>
                <li className="flex gap-2 items-center"><BrainCircuit className="w-4 h-4 text-enamel"/> Multimodal AI Pipeline</li>
              </ul>
            </div>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-center pt-12 border-t border-slate-100 gap-8">
            <div className="flex items-center gap-3 glass-panel px-6 py-3 rounded-full">
              <MapPin className="w-4 h-4 text-enamel" />
              <span className="text-[10px] font-black uppercase tracking-widest">Crafted in <span className="text-radiology font-black">St. Louis, MO</span></span>
            </div>
            <div className="text-[10px] font-black text-slate-300 uppercase tracking-widest">
               DentalTechup LLC // DBA Health XR © 2026
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}