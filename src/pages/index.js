import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title" style={{fontSize: '3.5rem', fontWeight: 'bold'}}>
          🤖 Physical AI & Humanoid Robotics
        </h1>
        <p className="hero__subtitle" style={{fontSize: '1.5rem', marginTop: '1rem'}}>
          Master the Future of Intelligent Machines
        </p>
        <p style={{fontSize: '1.1rem', marginTop: '1.5rem', opacity: 0.9}}>
          A comprehensive guide to Physical AI, robotics fundamentals, and building intelligent humanoid systems
        </p>
        <div style={{marginTop: '2rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap'}}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro"
            style={{fontSize: '1.2rem', padding: '0.8rem 2rem'}}>
            📚 Start Reading
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="https://github.com/Arham2005/GIAIC-Hackathon"
            style={{fontSize: '1.2rem', padding: '0.8rem 2rem'}}>
            ⭐ View on GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

function FeatureCard({icon, title, description}) {
  return (
    <div className={clsx('col col--4')} style={{marginBottom: '2rem'}}>
      <div style={{
        padding: '2rem',
        borderRadius: '12px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        height: '100%',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
        transition: 'transform 0.3s ease',
      }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-10px)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
        <div style={{fontSize: '3rem', marginBottom: '1rem'}}>{icon}</div>
        <h3 style={{fontSize: '1.5rem', marginBottom: '1rem'}}>{title}</h3>
        <p style={{fontSize: '1rem', opacity: 0.95}}>{description}</p>
      </div>
    </div>
  );
}

function ChapterHighlight({number, title, description, link}) {
  return (
    <div className={clsx('col col--6')} style={{marginBottom: '2rem'}}>
      <Link to={link} style={{textDecoration: 'none', color: 'inherit'}}>
        <div style={{
          padding: '1.5rem',
          border: '2px solid #e0e0e0',
          borderRadius: '10px',
          transition: 'all 0.3s ease',
          background: 'white',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.borderColor = '#667eea';
          e.currentTarget.style.boxShadow = '0 5px 20px rgba(102, 126, 234, 0.3)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.borderColor = '#e0e0e0';
          e.currentTarget.style.boxShadow = 'none';
        }}>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem'}}>
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              fontSize: '1.2rem'
            }}>
              {number}
            </div>
            <h3 style={{margin: 0, fontSize: '1.3rem'}}>{title}</h3>
          </div>
          <p style={{margin: 0, fontSize: '0.95rem', color: '#666'}}>{description}</p>
        </div>
      </Link>
    </div>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Learn Physical AI and Humanoid Robotics">
      <HomepageHeader />
      <main>
        {/* Features Section */}
        <section style={{padding: '4rem 0', background: '#f5f7fa'}}>
          <div className="container">
            <h2 style={{textAlign: 'center', fontSize: '2.5rem', marginBottom: '3rem'}}>
              ✨ What You'll Learn
            </h2>
            <div className="row">
              <FeatureCard
                icon="🧠"
                title="AI Fundamentals"
                description="Master the core concepts of artificial intelligence and machine learning for robotics applications"
              />
              <FeatureCard
                icon="🦾"
                title="Robotics Systems"
                description="Understand kinematics, dynamics, sensors, and actuators that bring robots to life"
              />
              <FeatureCard
                icon="🤖"
                title="Humanoid Design"
                description="Learn bipedal locomotion, manipulation, and human-robot interaction principles"
              />
            </div>
          </div>
        </section>

        {/* Featured Chapters */}
        <section style={{padding: '4rem 0'}}>
          <div className="container">
            <h2 style={{textAlign: 'center', fontSize: '2.5rem', marginBottom: '3rem'}}>
              📖 Featured Chapters
            </h2>
            <div className="row">
              <ChapterHighlight
                number="1"
                title="Introduction to Physical AI"
                description="Explore the convergence of AI with robotics and embodied systems"
                link="/docs/introduction-to-physical-ai"
              />
              <ChapterHighlight
                number="2"
                title="Robotics Fundamentals"
                description="Master degrees of freedom, coordinate systems, and mechanical principles"
                link="/docs/robotics-fundamentals"
              />
              <ChapterHighlight
                number="4"
                title="Kinematics & Dynamics"
                description="Understand robot motion, forces, and trajectory planning"
                link="/docs/kinematics-and-dynamics"
              />
              <ChapterHighlight
                number="7"
                title="Machine Learning for Robotics"
                description="Apply ML techniques for perception, control, and decision-making"
                link="/docs/machine-learning-for-robotics"
              />
            </div>
            <div style={{textAlign: 'center', marginTop: '2rem'}}>
              <Link
                className="button button--primary button--lg"
                to="/docs/intro">
                📚 Browse All Chapters →
              </Link>
            </div>
          </div>
        </section>

        {/* AI Assistant Section */}
        <section style={{padding: '4rem 0', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white'}}>
          <div className="container" style={{textAlign: 'center'}}>
            <h2 style={{fontSize: '2.5rem', marginBottom: '1.5rem'}}>
              💬 AI-Powered Learning Assistant
            </h2>
            <p style={{fontSize: '1.3rem', marginBottom: '2rem', opacity: 0.95}}>
              Ask questions, get explanations, and explore concepts with our integrated RAG chatbot
            </p>
            <div style={{fontSize: '3rem', marginBottom: '1rem'}}>🤖</div>
            <p style={{fontSize: '1.1rem', opacity: 0.9}}>
              Look for the chat button in the bottom-right corner while reading!
            </p>
          </div>
        </section>
      </main>
    </Layout>
  );
}