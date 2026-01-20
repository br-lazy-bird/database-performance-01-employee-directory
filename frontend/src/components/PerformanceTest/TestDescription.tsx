import React from 'react';

const TestDescription: React.FC = () => {
  return (
    <div className="description">
      <div className="dialogue">
        <img src="/lazy-bird.png" alt="Lazy Bird" className="mascot-icon" />
        <p>
          "So, this is the employee directory I mentioned in the <a href="https://github.com/br-lazy-bird/database-performance-01-employee-directory/blob/main/README.md#the-problem" target="_blank" rel="noopener noreferrer">README</a>...
          HR says searching for people is taking forever. We have a million employees in there and every search feels like watching paint dry.
          I'm pretty sure it's something in the database, but I have a very important appointment with my couch, so...
          could you run that performance test and see what you can find? Thanks!"
        </p>
      </div>
    </div>
  );
};

export default TestDescription;