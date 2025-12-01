import { useState } from 'react';
import { WaveGradientBackground } from './components/WaveGradientBackground';
import { LandingPage } from './components/LandingPage';
import { DecisionMaking } from './components/DecisionMaking';
import { Payment } from './components/Payment';
import { GlassFAB } from './components/GlassFAB';

/**
 * Figma Export Demo Page
 * 
 * This page displays all three main screens side-by-side for easy export to Figma.
 * You can:
 * 1. Use a Figma plugin like "html.to.design" to import this page
 * 2. Take screenshots of individual sections
 * 3. Use browser dev tools to inspect and copy styles
 */

export default function FigmaExport() {
  const [activeView, setActiveView] = useState<'all' | 'landing' | 'decision' | 'payment'>('all');

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      {/* View Selector */}
      <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex gap-2 bg-gray-800/90 backdrop-blur-lg rounded-full p-2 shadow-lg">
        <button
          onClick={() => setActiveView('all')}
          className={`px-4 py-2 rounded-full text-sm transition-all ${
            activeView === 'all'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          All Views
        </button>
        <button
          onClick={() => setActiveView('landing')}
          className={`px-4 py-2 rounded-full text-sm transition-all ${
            activeView === 'landing'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Landing
        </button>
        <button
          onClick={() => setActiveView('decision')}
          className={`px-4 py-2 rounded-full text-sm transition-all ${
            activeView === 'decision'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Decision
        </button>
        <button
          onClick={() => setActiveView('payment')}
          className={`px-4 py-2 rounded-full text-sm transition-all ${
            activeView === 'payment'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Payment
        </button>
      </div>

      {/* Content Area */}
      <div className="mt-16">
        {activeView === 'all' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {/* Landing Page */}
            <div className="flex flex-col">
              <h2 className="text-white text-xl mb-4 text-center">Landing Page</h2>
              <div className="w-full max-w-md mx-auto h-[812px] relative overflow-hidden rounded-[32px] shadow-2xl border border-gray-700">
                <div className="absolute inset-0">
                  <WaveGradientBackground />
                </div>
                <div className="relative z-10">
                  <LandingPage onDoubleTap={() => console.log('Double tap')} />
                  <div className="absolute bottom-8 left-0 right-0 flex justify-center pointer-events-none">
                    <div className="pointer-events-auto">
                      <GlassFAB
                        onVoiceCommand={() => {}}
                        onTextMessage={() => {}}
                        onScreenshot={() => {}}
                        onSend={() => {}}
                        isChatActive={false}
                        onExpandedChange={() => {}}
                        isTalking={false}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Decision Making */}
            <div className="flex flex-col">
              <h2 className="text-white text-xl mb-4 text-center">Decision Making</h2>
              <div className="w-full max-w-md mx-auto h-[812px] relative overflow-hidden rounded-[32px] shadow-2xl border border-gray-700">
                <div className="absolute inset-0">
                  <WaveGradientBackground />
                </div>
                <div className="relative z-10">
                  <DecisionMaking onSelect={() => console.log('Selected')} />
                  <div className="absolute bottom-8 left-0 right-0 flex justify-center pointer-events-none">
                    <div className="pointer-events-auto">
                      <GlassFAB
                        onVoiceCommand={() => {}}
                        onTextMessage={() => {}}
                        onScreenshot={() => {}}
                        onSend={() => {}}
                        isChatActive={false}
                        onExpandedChange={() => {}}
                        isTalking={false}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment */}
            <div className="flex flex-col">
              <h2 className="text-white text-xl mb-4 text-center">Payment</h2>
              <div className="w-full max-w-md mx-auto h-[812px] relative overflow-hidden rounded-[32px] shadow-2xl border border-gray-700">
                <div className="absolute inset-0">
                  <WaveGradientBackground />
                </div>
                <div className="relative z-10 h-full flex items-center justify-center">
                  <Payment
                    selectedPlan={1}
                    onComplete={() => console.log('Payment complete')}
                    onBack={() => console.log('Back')}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Individual Views */}
        {activeView === 'landing' && (
          <div className="max-w-md mx-auto">
            <h2 className="text-white text-2xl mb-6 text-center">Landing Page</h2>
            <div className="w-full h-[812px] relative overflow-hidden rounded-[32px] shadow-2xl border border-gray-700">
              <div className="absolute inset-0">
                <WaveGradientBackground />
              </div>
              <div className="relative z-10">
                <LandingPage onDoubleTap={() => console.log('Double tap')} />
                <div className="absolute bottom-8 left-0 right-0 flex justify-center pointer-events-none">
                  <div className="pointer-events-auto">
                    <GlassFAB
                      onVoiceCommand={() => {}}
                      onTextMessage={() => {}}
                      onScreenshot={() => {}}
                      onSend={() => {}}
                      isChatActive={false}
                      onExpandedChange={() => {}}
                      isTalking={false}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeView === 'decision' && (
          <div className="max-w-md mx-auto">
            <h2 className="text-white text-2xl mb-6 text-center">Decision Making</h2>
            <div className="w-full h-[812px] relative overflow-hidden rounded-[32px] shadow-2xl border border-gray-700">
              <div className="absolute inset-0">
                <WaveGradientBackground />
              </div>
              <div className="relative z-10">
                <DecisionMaking onSelect={() => console.log('Selected')} />
                <div className="absolute bottom-8 left-0 right-0 flex justify-center pointer-events-none">
                  <div className="pointer-events-auto">
                    <GlassFAB
                      onVoiceCommand={() => {}}
                      onTextMessage={() => {}}
                      onScreenshot={() => {}}
                      onSend={() => {}}
                      isChatActive={false}
                      onExpandedChange={() => {}}
                      isTalking={false}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeView === 'payment' && (
          <div className="max-w-md mx-auto">
            <h2 className="text-white text-2xl mb-6 text-center">Payment</h2>
            <div className="w-full h-[812px] relative overflow-hidden rounded-[32px] shadow-2xl border border-gray-700">
              <div className="absolute inset-0">
                <WaveGradientBackground />
              </div>
              <div className="relative z-10 h-full flex items-center justify-center">
                <Payment
                  selectedPlan={1}
                  onComplete={() => console.log('Payment complete')}
                  onBack={() => console.log('Back')}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="fixed bottom-4 left-4 max-w-md bg-gray-800/90 backdrop-blur-lg rounded-2xl p-4 text-white text-sm shadow-lg">
        <h3 className="font-semibold mb-2">Export to Figma:</h3>
        <ol className="list-decimal list-inside space-y-1 text-gray-300">
          <li>Install "html.to.design" plugin in Figma</li>
          <li>Copy the URL of this page</li>
          <li>Paste in the plugin to import all components</li>
          <li>Or take screenshots for manual import</li>
        </ol>
      </div>
    </div>
  );
}
