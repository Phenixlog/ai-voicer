import { Navbar } from '../components/landing/Navbar';
import { Hero } from '../components/landing/Hero';
import { FeaturesGrid } from '../components/landing/FeaturesGrid';
import { HowItWorks } from '../components/landing/HowItWorks';
import { Pricing } from '../components/landing/Pricing';
import { FAQ } from '../components/landing/FAQ';
import { Footer } from '../components/landing/Footer';

export const LandingPage = () => {
  return (
    <div className="bg-white text-slate-900">
      <Navbar />
      <main>
        <Hero />
        <HowItWorks />
        <FeaturesGrid />
        <Pricing />
        <FAQ />
      </main>
      <Footer />
    </div>
  );
};
